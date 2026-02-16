# Collector System

Collectors are pluggable modules that gather batches of URLs from external sources. Each collector runs asynchronously and feeds URLs into the pipeline for automated enrichment and human annotation.

## Available Collectors

| Collector | Type Key | Source |
|-----------|----------|--------|
| **Common Crawler** | `COMMON_CRAWLER` | Interfaces with the Common Crawl dataset to extract URLs |
| **Auto-Googler** | `AUTO_GOOGLER` | Automates Google Custom Search API to find URLs |
| **CKAN** | `CKAN` | Scrapes packages from CKAN open data portals |
| **MuckRock Simple Search** | `MUCKROCK_SIMPLE_SEARCH` | Searches MuckRock FOIA requests |
| **MuckRock County Search** | `MUCKROCK_COUNTY_SEARCH` | County-level MuckRock FOIA search |
| **MuckRock All FOIA** | `MUCKROCK_ALL_SEARCH` | Retrieves all MuckRock FOIA requests |
| **Example** | `EXAMPLE` | A reference implementation for development |

Each collector has its own README in `src/collectors/impl/<name>/`.

## Architecture

```
src/collectors/
├── manager.py          # AsyncCollectorManager — starts, stops, tracks collectors
├── mapping.py          # COLLECTOR_MAPPING — registry of collector types to classes
├── enums.py            # CollectorType enum
├── exceptions.py       # Custom exceptions
├── queries/            # Collector-specific database queries
└── impl/
    ├── base.py         # AsyncCollectorBase — abstract base class
    ├── auto_googler/
    ├── ckan/
    ├── common_crawler/
    ├── example/
    └── muckrock/
```

### AsyncCollectorManager

The `AsyncCollectorManager` is responsible for:

- Starting collectors as async tasks.
- Tracking running collectors by batch ID.
- Aborting collectors on request.
- Shutting down all collectors on app shutdown.

It is initialized during app startup and linked to the task manager, so that when a collector finishes, URL processing tasks are automatically triggered.

### AsyncCollectorBase

All collectors inherit from `AsyncCollectorBase`. The base class handles:

- **Lifecycle management** — timing, status tracking, error handling.
- **Logging** — writes log entries to the database via `AsyncCoreLogger`.
- **Post-processing** — after `run_implementation()` completes, the base class runs a preprocessor to normalize the output, inserts URLs into the database, updates the batch record, and triggers downstream tasks.

The lifecycle is:

```
run()
  ├── start_timer()
  ├── run_implementation()      # <-- your code here
  ├── stop_timer()
  ├── close()                   # sets status to READY_TO_LABEL
  └── process()
       ├── preprocessor.preprocess()    # normalize output
       ├── adb_client.insert_urls()     # insert into DB
       ├── adb_client.update_batch_post_collection()  # update batch
       └── post_collection_function_trigger.trigger()  # trigger URL tasks
```

If the collector is cancelled, status is set to `ABORTED`. If an exception occurs, status is set to `ERROR`.

## Creating a New Collector

### 1. Create the Collector Class

Create a new directory under `src/collectors/impl/` and implement a class that inherits from `AsyncCollectorBase`:

```python
from src.collectors.impl.base import AsyncCollectorBase
from src.collectors.enums import CollectorType
from src.core.preprocessors.base import PreprocessorBase

class MyCollector(AsyncCollectorBase):
    collector_type = CollectorType.MY_COLLECTOR
    preprocessor = MyPreprocessor  # must extend PreprocessorBase

    async def run_implementation(self) -> None:
        # Your collection logic here.
        # Use self.dto to access input parameters.
        # Use await self.log("message") to write log entries.
        # Set self.data to the collected output (a Pydantic model).
        pass
```

### 2. Create a Preprocessor

The preprocessor converts your collector's raw output into a list of `URLInfo` objects. Create a class extending `PreprocessorBase` in `src/core/preprocessors/`:

```python
from src.core.preprocessors.base import PreprocessorBase
from src.db.models.impl.url.core.pydantic.info import URLInfo

class MyPreprocessor(PreprocessorBase):
    def preprocess(self, data) -> list[URLInfo]:
        # Convert raw data into URLInfo objects
        pass
```

### 3. Add to the Collector Mapping

Register your collector in `src/collectors/mapping.py`:

```python
from src.collectors.impl.my_collector.collector import MyCollector

COLLECTOR_MAPPING = {
    # ... existing collectors ...
    CollectorType.MY_COLLECTOR: MyCollector,
}
```

### 4. Add the Enum Value

Add your collector type to `CollectorType` in `src/collectors/enums.py`.

### 5. Create an API Endpoint

Add a POST endpoint in `src/api/endpoints/collector/routes.py` to trigger your collector. Follow the pattern of existing collector endpoints.

### 6. Create a Request DTO

Define a Pydantic model for the collector's input parameters. This is passed as `self.dto` in the collector.

## Batch Lifecycle

When a collector is started via the API:

1. A new batch record is created in the database with status `IN_PROCESS`.
2. The collector runs asynchronously.
3. On success, the batch status becomes `READY_TO_LABEL` and URL tasks are triggered.
4. On error, the batch status becomes `ERROR`.
5. On abort, the batch status becomes `ABORTED`.

Batches can be viewed, filtered, and managed through the `/batch` API endpoints.
