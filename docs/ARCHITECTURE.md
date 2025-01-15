## Architecture Design

### Separation of Concerns

The library is structured with clear separation of concerns across three client types (Update and Delete Clients in Development):

1. **BaseClient**
   - Handles core HTTP communication with SharePoint
   - Manages authentication and token lifecycle
   - Provides common utilities (URL formatting, request handling, path parsing)
   - Handles low-level error handling and logging
   - Acts as the infrastructure layer

2. **ReadClient**
   - Focuses solely on read operations (GET requests)
   - Implements business logic for retrieving SharePoint resources
   - Uses BaseClient for HTTP operations
   - Logs only business-level events
   - No direct HTTP or authentication handling

3. **CreateClient**
   - Focuses solely on write operations (POST/PUT requests)
   - Implements business logic for creating SharePoint resources
   - Uses BaseClient for HTTP operations
   - Logs only business-level events
   - No direct HTTP or authentication handling

### Client Factory Pattern

1. Centralized Client Management
   -The `ClientFactory` class centralizes the creation and management of client instances (`BaseClient`, `ReadClient`, and `CreateClient`). This ensures:

   - **Consistency**: All clients are instantiated and reused in a standardized way.
   - **Optimized Performance**: By sharing a single instance of `BaseClient`, redundant initializations, such as fetching access tokens multiple times, are avoided.

2. Singleton Pattern
   - The Singleton pattern implemented in `ClientFactory` provides the following benefits:

   - **A Single Instance**: Only one instance of `BaseClient` is created and shared across `ReadClient` and `CreateClient`. This minimizes resource usage and ensures a consistent application state.
   - **Thread Safety**: The use of `threading.Lock` ensures thread-safe Singleton implementation, avoiding race conditions when multiple threads try to create a `BaseClient` instance simultaneously.
   - **Configuration Change Management**: The `reset_base_client` method allows resetting the Singleton instance when configuration changes, providing flexibility while retaining the benefits of the pattern.

3. Separation of Concerns
   - `BaseClient`: Handles low-level communication with the Microsoft Graph API, such as managing access tokens and making HTTP requests.
   - `ReadClient` and `CreateClient`: Focus on business-specific operations, like reading site and drive details or creating folders.


4. Code Reusability
   - The `ClientFactory` class promotes reusability by:

   - Providing factory methods to create `ReadClient` and `CreateClient` instances.
   - Avoiding duplication of initialization logic across the application.

5. Performance Optimization
   - Sharing a single `BaseClient` instance reduces memory usage and network overhead.
   - Avoids repeated token fetching and configuration parsing for each client instance.

6. Improved Logging and Error Handling
   - **Centralized Error Handling**: Errors during `BaseClient` initialization are logged consistently in the `get_base_client` method, simplifying debugging.
   - **Context-Specific Logs**: Logs in `ReadClient` and `CreateClient` focus on higher-level business logic without duplicating low-level logs from `BaseClient`.

7. Scalability
   - Adding new client types (e.g., `DeleteClient`, `UpdateClient`) is straightforward. Simply extend `ClientFactory` with new factory methods, ensuring these clients also share the `BaseClient` instance.
   - This modular architecture supports future growth and easy integration with additional APIs or business requirements.

---
