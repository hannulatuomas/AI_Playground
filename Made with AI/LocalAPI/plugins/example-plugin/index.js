/**
 * Example Plugin for LocalAPI
 * 
 * This plugin demonstrates:
 * - Lifecycle hooks (onLoad, onUnload)
 * - Request/Response hooks
 * - Using the plugin context API
 * - Storing plugin data
 */

module.exports = {
  /**
   * Called when plugin is loaded
   */
  async onLoad(context) {
    context.api.log('Example plugin loaded!');
    context.api.notify('Example plugin is now active', 'success');

    // Store some data
    await context.api.storage.set('loadCount', 
      (await context.api.storage.get('loadCount') || 0) + 1
    );

    const loadCount = await context.api.storage.get('loadCount');
    context.api.log(`This plugin has been loaded ${loadCount} time(s)`);
  },

  /**
   * Called when plugin is unloaded
   */
  async onUnload(context) {
    context.api.log('Example plugin unloaded');
    context.api.notify('Example plugin has been deactivated', 'info');
  },

  /**
   * Called before a request is sent
   * Can modify the request
   */
  async onBeforeRequest(request, context) {
    context.api.log('Before request:', request.method, request.url);

    // Example: Add a custom header to all requests
    if (!request.headers) {
      request.headers = [];
    }

    request.headers.push({
      key: 'X-Plugin-Example',
      value: 'Added by example plugin',
      enabled: true
    });

    // Example: Log request details
    await context.api.storage.set('lastRequest', {
      method: request.method,
      url: request.url,
      timestamp: new Date().toISOString()
    });

    return request;
  },

  /**
   * Called after a response is received
   * Can modify the response
   */
  async onAfterResponse(response, request, context) {
    context.api.log('After response:', response.status, response.statusText);

    // Example: Track response times
    const responseTimes = await context.api.storage.get('responseTimes') || [];
    responseTimes.push({
      url: request.url,
      time: response.time,
      status: response.status,
      timestamp: new Date().toISOString()
    });

    // Keep only last 100 entries
    if (responseTimes.length > 100) {
      responseTimes.shift();
    }

    await context.api.storage.set('responseTimes', responseTimes);

    // Example: Show notification for slow requests
    if (response.time > 1000) {
      context.api.notify(
        `Slow request detected: ${request.url} took ${response.time}ms`,
        'warning'
      );
    }

    return response;
  },

  /**
   * Called when a collection is created
   */
  async onCollectionCreate(collection, context) {
    context.api.log('Collection created:', collection.name);
  },

  /**
   * Called when a collection is updated
   */
  async onCollectionUpdate(collection, context) {
    context.api.log('Collection updated:', collection.name);
  },

  /**
   * Called when a collection is deleted
   */
  async onCollectionDelete(collectionId, context) {
    context.api.log('Collection deleted:', collectionId);
  }
};
