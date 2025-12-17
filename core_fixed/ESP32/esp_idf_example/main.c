#include <string.h>
#include "esp_log.h"
#include "esp_system.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "esp_tls.h"
#include "esp_http_client.h"

static const char *TAG = "esp_idf_spoon";

// Replace with your server root CA PEM if available
static const char *server_root_ca = "-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n";

esp_err_t _http_event_handler(esp_http_client_event_t *evt) {
    switch(evt->event_id) {
        case HTTP_EVENT_ON_DATA:
            if (!esp_http_client_is_chunked_response(evt->client)) {
                printf("Response: %.*s\n", evt->data_len, (char*)evt->data);
            }
            break;
        default:
            break;
    }
    return ESP_OK;
}

void post_meal(const char *url, const char *device_token, const char *json_payload) {
    esp_http_client_config_t config = {
        .url = url,
        .event_handler = _http_event_handler,
        .transport_type = HTTP_TRANSPORT_OVER_SSL,
        .crt_bundle_attach = NULL, // use server_root_ca below
    };
    esp_http_client_handle_t client = esp_http_client_init(&config);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    char auth_header[256];
    snprintf(auth_header, sizeof(auth_header), "Token %s", device_token);
    esp_http_client_set_header(client, "Authorization", auth_header);
    esp_http_client_set_post_field(client, json_payload, strlen(json_payload));

    // If you have root CA, use esp_tls_set_global_ca_store or set in config
    esp_http_client_perform(client);
    esp_http_client_cleanup(client);
}

void app_main(void) {
    // Initialize network/WiFi before calling post_meal
    const char *url = "https://your-public-host.example.com/dashboard/api/sodium/add-meal/";
    const char *token = "REPLACE_WITH_DEVICE_UUID_TOKEN";
    const char *payload = "{\"name\":\"spoon-meal\",\"sodium_mg\":123}";
    ESP_LOGI(TAG, "Posting meal...");
    post_meal(url, token, payload);
}
