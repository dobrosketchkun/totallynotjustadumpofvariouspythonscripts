function setDropdown(){
var num
var sheet = SpreadsheetApp.getActiveSheet();
let nums = [1,2,3,4,5,6,7,8,9] // values of drop-down list
var arrayLength = nums.length;

for (var i = 0; i < arrayLength; i++) { // setting up the sheet
    num = nums[i]
    console.log(num);
    var coord = 'A' + num.toString(10);
    console.log(coord);
    sheet.getRange(coord).setValue(num)
}

var dynamicList = sheet.getRange('A1:A9'); // reading values
var arrayValues = dynamicList.getValues();
var rangeRule = SpreadsheetApp.newDataValidation().requireValueInList(arrayValues);
sheet.getRange('B1').setDataValidation(rangeRule); // place the drop-down list


}
