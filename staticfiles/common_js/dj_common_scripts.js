// enter only number in input text field
var strToNumber = document.querySelector('.textToNumbers');
strToNumber.addEventListener('input', restrictNumber);
function restrictNumber(e) {
    var newValue = this.value.replace(new RegExp(/[^\d]/, 'ig'), "");
    this.value = newValue;
}