let spreadsheet = SpreadsheetApp.openById("1bJkvL9R3L-rQCbdfX5OGKV9tk4pu-KEF6LqPggJIaAI")

function doPost(e){
  addReading(e);
}

function addReading(e) {
  let data = JSON.parse(e.postData.contents);
  let mac = data.mac
  var sheet = spreadsheet.getSheetByName(mac);

  if (!sheet) {
   spreadsheet.insertSheet(mac);
   sheet = spreadsheet.getSheetByName(mac);
   sheet.appendRow(["UTC Time (GMT +0)" ,'MAC address', 'Temperature (°C)', 'Relative Humidity', 'Battery' ])
   var headerRange = sheet.getRange(1, 1, 1, sheet.getLastColumn());
   headerRange.setFontWeight('bold')
  }
  
  sheet.appendRow([data.UTCtimestamp,data.mac,data.temp, data.humidity, data.battery])
  return ContentService.createTextOutput('Success')
}