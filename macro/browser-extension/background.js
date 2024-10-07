// Helper function to send tab URL to Python server
function sendTabUrlToServer(url) {
    fetch('http://127.0.0.1:7853/active-tab', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url }),
    })
}

// Detect when a tab becomes active (user switches tabs)
chrome.tabs.onActivated.addListener(function(activeInfo) {
    chrome.tabs.get(activeInfo.tabId, function(tab) {
        var activeUrl = tab.url;
        console.log("Tab switched. Active Tab URL:", activeUrl);

        // Send the active tab's URL to your Python app via fetch
        sendTabUrlToServer(activeUrl);
    });
});

// Detect when the URL of the active tab changes
chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
    var activeUrl = changeInfo.url;
    if (activeUrl) {
        console.log("Tab URL changed. New URL:", activeUrl);

        // Send the updated tab URL to your Python app via fetch
        sendTabUrlToServer(activeUrl);
    }
});