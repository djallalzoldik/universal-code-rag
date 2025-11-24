// Sample JavaScript file for testing

class ChromeExtension {
  constructor(extensionId) {
    this.extensionId = extensionId;
    this.permissions = [];
  }
  
  async requestPermissions(permissions) {
    return new Promise((resolve, reject) => {
      chrome.permissions.request(
        { permissions: permissions },
        (granted) => {
          if (granted) {
            this.permissions.push(...permissions);
            resolve(true);
          } else {
            reject(new Error('Permission denied'));
          }
        }
      );
    });
  }
  
  hasPermission(permission) {
    return this.permissions.includes(permission);
  }
  
  static validateExtensionId(id) {
    const pattern = /^[a-z]{32}$/;
    return pattern.test(id);
  }
}

const sendMessage = (message, callback) => {
  chrome.runtime.sendMessage(message, (response) => {
    if (chrome.runtime.lastError) {
      console.error(chrome.runtime.lastError);
      return;
    }
    callback(response);
  });
};

export { ChromeExtension, sendMessage };
