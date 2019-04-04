/**
 * Performs a real-time check of whether the username is free or not, displaying
 * either a tick (yes it is available) or a cross (not it is not available). the
 * request is performed using AJAX and a JSON request object and response. The
 * response will return a JSON object with an exists field set to either:
 *    True - the name exists and is not available
 *    False - the name does not exist and is available
 */
var REGEXP_LT = /</g;
var REGEXP_GT = />/g;
function checkUsername(userElem) {
  var xhr = new XMLHttpRequest()
  xhr.onload = function() {
    var jsonresp = JSON.parse(xhr.response);
    if (jsonresp.exists) {
      document.getElementById("usercheck").innerHTML = "&#10060;"
    } else {
      document.getElementById("usercheck").innerHTML = "&#9989;"
    }
  }
  xhr.open("POST", "/username");
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.send(JSON.stringify({
    /**
     * VULN Client Reflected XSS, assuming that all input is unsafe
     */
    "username": escapeHtml(userElem.value)
  }));
  return false;
}

function escapeHtml(html) {
  return html.replace(REGEXP_LT, "&lt;").replace(REGEXP_GT, "&gt;");
}