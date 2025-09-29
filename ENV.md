This page provides a full list, with description, of all the environment variables used by the application.

Please ensure these are properly defined in a `.env` file in the root directory.

| Name                            | Description                                                                                                                                                                   | Example                                                                                      |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------|
| `GOOGLE_API_KEY`                | The API key required for accessing the Google Custom Search API                                                                                                               | `abc123`                                                                                     |
| `GOOGLE_CSE_ID`                 | The CSE ID required for accessing the Google Custom Search API                                                                                                                | `abc123`                                                                                     |
| `POSTGRES_USER`                 | The username for the test database                                                                                                                                            | `test_source_collector_user`                                                                 |
| `POSTGRES_PASSWORD`             | The password for the test database                                                                                                                                            | `HanviliciousHamiltonHilltops`                                                               |
| `POSTGRES_DB`                   | The database name for the test database                                                                                                                                       | `source_collector_test_db`                                                                   |
| `POSTGRES_HOST`                 | The host for the test database                                                                                                                                                | `127.0.0.1`                                                                                  |
| `POSTGRES_PORT`                 | The port for the test database                                                                                                                                                | `5432`                                                                                       |
| `DS_APP_SECRET_KEY`             | The secret key used for decoding JWT tokens produced by the Data Sources App. Must match the secret token `JWT_SECRET_KEY` that is used in the Data Sources App for encoding. | `abc123`                                                                                     |
| `DEV`                           | Set to any value to run the application in development mode.                                                                                                                  | `true`                                                                                       |
| `DEEPSEEK_API_KEY`              | The API key required for accessing the DeepSeek API.                                                                                                                          | `abc123`                                                                                     |
| `OPENAI_API_KEY`                | The API key required for accessing the OpenAI API.                                                                                                                            | `abc123`                                                                                     |
| `PDAP_EMAIL`                    | An email address for accessing the PDAP API.[^1]                                                                                                                              | `abc123@test.com`                                                                            |
| `PDAP_PASSWORD`                 | A password for accessing the PDAP API.[^1]                                                                                                                                    | `abc123`                                                                                     |
| `PDAP_API_KEY`                  | An API key for accessing the PDAP API.                                                                                                                                        | `abc123`                                                                                     |
| `PDAP_API_URL`                  | The URL for the PDAP API                                                                                                                                                      | `https://data-sources-v2.pdap.dev/api`                                                       |
| `DISCORD_WEBHOOK_URL`           | The URL for the Discord webhook used for notifications                                                                                                                        | `abc123`                                                                                     |
| `HUGGINGFACE_INFERENCE_API_KEY` | The API key required for accessing the Hugging Face Inference API.                                                                                                            | `abc123`                                                                                     |
| `HUGGINGFACE_HUB_TOKEN`         | The API key required for uploading to the PDAP HuggingFace account via Hugging Face Hub API.                                                                                                                                                                     | `abc123`  |
| `INTERNET_ARCHIVE_S3_KEYS`      | Keys used for saving a URL to the Internet Archives.   | 'abc123:gpb0dk` |



[^1:] The user account in question will require elevated permissions to access certain endpoints. At a minimum, the user will require the `source_collector` and `db_write` permissions.

# Variables With Defaults

The following environment variables have default values that will be used if not otherwise defined.

| Variable                      | Description                                                      | Default |
|-------------------------------|------------------------------------------------------------------|---------|
| `URL_TASKS_FREQUENCY_MINUTES` | The frequency for the `RUN_URL_TASKS` Scheduled Task, in minutes | `60`    |

# Flags

Flags are used to enable/disable certain features. They are set to `1` to enable the feature and `0` to disable the feature. By default, all flags are enabled.

## Configuration Flags

Configuration flags are used to enable/disable certain configurations.

| Flag         | Description                          |
|--------------|--------------------------------------|
| `POST_TO_DISCORD_FLAG` | Enables posting errors to discord.   |
| `PROGRESS_BAR_FLAG` | Enables progress bars on some tasks. |


## Task Flags
Task flags are used to enable/disable certain tasks. 

Note that some tasks/subtasks are themselves enabled by other tasks.

### Scheduled Task Flags

| Flag                                | Description                                                        |
|-------------------------------------|--------------------------------------------------------------------|
| `SCHEDULED_TASKS_FLAG`              | All scheduled tasks. Disabling disables all other scheduled tasks. |
| `PUSH_TO_HUGGING_FACE_TASK_FLAG`    | Pushes data to HuggingFace.                            |
| `POPULATE_BACKLOG_SNAPSHOT_TASK_FLAG` | Populates the backlog snapshot.                        |
| `DELETE_OLD_LOGS_TASK_FLAG`         | Deletes old logs.                                      |
| `RUN_URL_TASKS_TASK_FLAG`           | Runs URL tasks.                                        |
| `IA_PROBE_TASK_FLAG`            | Extracts and links Internet Archives metadata to URLs. |
| `IA_SAVE_TASK_FLAG`             | Saves URLs to Internet Archives.                       |

### URL Task Flags

URL Task Flags are collectively controlled by the `RUN_URL_TASKS_TASK_FLAG` flag.


| Flag                                | Description                                           |
|-------------------------------------|-------------------------------------------------------|
| `URL_HTML_TASK_FLAG`                | URL HTML scraping task.                               |
| `URL_RECORD_TYPE_TASK_FLAG`         | Automatically assigns Record Types to URLs.           |
| `URL_AGENCY_IDENTIFICATION_TASK_FLAG` | Automatically assigns and suggests Agencies for URLs. |
| `URL_SUBMIT_APPROVED_TASK_FLAG`     | Submits approved URLs to the Data Sources App.        |
| `URL_MISC_METADATA_TASK_FLAG`       | Adds misc metadata to URLs.                           |
| `URL_404_PROBE_TASK_FLAG`           | Probes URLs for 404 errors.                           |
| `URL_AUTO_RELEVANCE_TASK_FLAG`      | Automatically assigns Relevances to URLs.             |
| `URL_PROBE_TASK_FLAG`               | Probes URLs for web metadata.                         |
| `URL_ROOT_URL_TASK_FLAG`            | Extracts and links Root URLs to URLs.                 |
| `URL_SCREENSHOT_TASK_FLAG`          | Takes screenshots of URLs.                            |
| `URL_AUTO_VALIDATE_TASK_FLAG`       | Automatically validates URLs.                         |
| `URL_AUTO_NAME_TASK_FLAG`           | Automatically names URLs.                             |
| `URL_SUSPEND_TASK_FLAG`             | Suspends URLs meeting suspension criteria.            |

### Agency ID Subtasks

Agency ID Subtasks are collectively disabled by the `URL_AGENCY_IDENTIFICATION_TASK_FLAG` flag.

| Flag                                | Description                                                       |
|-------------------------------------|-------------------------------------------------------------------|
| `AGENCY_ID_HOMEPAGE_MATCH_FLAG`     | Enables the homepage match subtask for agency identification.     |
| `AGENCY_ID_NLP_LOCATION_MATCH_FLAG` | Enables the NLP location match subtask for agency identification. |
| `AGENCY_ID_CKAN_FLAG`               | Enables the CKAN subtask for agency identification.               |
| `AGENCY_ID_MUCKROCK_FLAG`           | Enables the MuckRock subtask for agency identification.           |


### Location ID Subtasks

Location ID Subtasks are collectively disabled by the `URL_LOCATION_IDENTIFICATION_TASK_FLAG` flag

| Flag                                  | Description                                                         | 
|---------------------------------------|---------------------------------------------------------------------| 
| `LOCATION_ID_NLP_LOCATION_MATCH_FLAG` | Enables the NLP location match subtask for location identification. |


## Foreign Data Wrapper (FDW)
```
FDW_DATA_SOURCES_HOST=127.0.0.1  # The host of the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_PORT=1234                  # The port of the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_USER=fdw_user           # The username for the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_PASSWORD=password          # The password for the Data Sources Database, used for FDW setup
FDW_DATA_SOURCES_DB=db_name                  # The database name for the Data Sources Database, used for FDW setup

```

## Data Dumper

```
PROD_DATA_SOURCES_HOST=127.0.0.1  # The host of the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_PORT=1234                  # The port of the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_USER=dump_user           # The username for the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_PASSWORD=password          # The password for the production Data Sources Database, used for Data Dumper
PROD_DATA_SOURCES_DB=db_name                  # The database name for the production Data Sources Database, used for Data Dumper
```