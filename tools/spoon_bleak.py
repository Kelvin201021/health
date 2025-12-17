#!/usr/bin/env python3
"""Connect to a BLE salt-sensing spoon, convert readings to mg, and POST to Django API.

Usage:
  python tools/spoon_bleak.py --token <DEVICE_TOKEN> [--address AA:BB:CC...] [--api-url URL]

Defaults assume the API endpoint at /dashboard/api/sodium/add-meal/ and example UUIDs.
Replace SERVICE_UUID and CHAR_UUID with your device's GATT UUIDs.
"""
import asyncio
import struct
import time
import os
import argparse
import logging

import requests
from bleak import BleakScanner, BleakClient

# Example/default UUIDs — replace with your spoon's values
DEFAULT_SERVICE_UUID = "0000feed-0000-1000-8000-00805f9b34fb"
DEFAULT_CHAR_UUID = "0000beef-0000-1000-8000-00805f9b34fb"

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def parse_measurement(data: bytearray) -> float:
    """Try uint16 then float32. Returns conductivity in µS/cm (example)."""
    if len(data) >= 2:
        try:
            return float(struct.unpack_from('<H', data)[0])
        except Exception:
            pass
    if len(data) >= 4:
        try:
            return float(struct.unpack_from('<f', data)[0])
        except Exception:
            pass
    # fallback: try first byte
    if len(data) >= 1:
        return float(data[0])
    return 0.0


async def run(args):
    token = args.token or os.environ.get('SPOON_TOKEN')
    if not token:
        raise SystemExit('Device token required (arg --token or env SPOON_TOKEN)')

    api_url = args.api_url.rstrip('/') + '/dashboard/api/sodium/add-meal/' if args.api_url else 'http://127.0.0.1:8000/dashboard/api/sodium/add-meal/'

    # choose device
    target = None
    if args.address:
        logging.info('Using provided address %s', args.address)
        target = args.address
    else:
        logging.info('Scanning for BLE devices (5s)...')
        devices = await BleakScanner.discover(timeout=5.0)
        for d in devices:
            name = (d.name or '').lower()
            if 'spoon' in name or 'salt' in name or 'kitchen' in name:
                target = d.address
                logging.info('Found candidate: %s (%s)', d.name, d.address)
                break
        if not target and devices:
            # pick first device as fallback
            target = devices[0].address

    if not target:
        raise SystemExit('No BLE device found')

    async with BleakClient(target) as client:
        logging.info('Connected: %s', client.is_connected)

        def handle(sender, data):
            cond = parse_measurement(data)
            mg = max(0, round(args.a * cond + args.b))
            payload = {
                'name': args.name or 'Spoon reading',
                'sodium_mg': int(mg),
                'portion': args.portion or 'spoon',
                'source': 'spoon',
                'recorded_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
            }
            headers = {
                'Authorization': f'Token {token}',
                'Content-Type': 'application/json',
            }
            try:
                r = requests.post(api_url, json=payload, headers=headers, timeout=8)
                logging.info('Posted %d mg → %s (%s)', mg, r.status_code, r.text[:200])
            except Exception as e:
                logging.warning('Failed to POST reading: %s', e)

        logging.info('Starting notifications on %s', args.char_uuid)
        await client.start_notify(args.char_uuid, handle)
        logging.info('Listening for %s seconds...', args.duration)
        try:
            await asyncio.sleep(args.duration)
        finally:
            await client.stop_notify(args.char_uuid)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', help='BLE address of the spoon (optional)')
    parser.add_argument('--service-uuid', dest='service_uuid', default=DEFAULT_SERVICE_UUID)
    parser.add_argument('--char-uuid', dest='char_uuid', default=DEFAULT_CHAR_UUID)
    parser.add_argument('--token', help='Device token (or set SPOON_TOKEN env var)')
    parser.add_argument('--api-url', help='Base site URL (e.g., https://example.com)')
    parser.add_argument('--a', type=float, default=0.8, help='Calibration coefficient a')
    parser.add_argument('--b', type=float, default=10.0, help='Calibration offset b')
    parser.add_argument('--duration', type=int, default=120, help='Listen time in seconds')
    parser.add_argument('--name', help='Name to send with readings')
    parser.add_argument('--portion', help='Portion text to send', default='spoon')
    args = parser.parse_args()

    # map names to chars (Bleak uses characteristic UUID directly)
    args.char_uuid = args.char_uuid or DEFAULT_CHAR_UUID
    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        logging.info('Interrupted')


if __name__ == '__main__':
    main()
