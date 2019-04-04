/**
 * Submits a search using an AJAX request that returns a JSON array of results.
 * Renders the results as new messages and inserts into the document.
 */
var REGEXP_LT = /</g;
var REGEXP_GT = />/g;

function submitSearch(oFormElement) {
  var xhr = new XMLHttpRequest(oFormElement);
  xhr.onload = function() {
    var jsonresp = JSON.parse(xhr.response);
    var resultString = "";
    for (var result of jsonresp) {
      /**
       * VULN  Client Reflected XSS, prevent client input,escapeHtml function helps filter '<>'
       */
      resultString = resultString + "<div class='resultitem'><p><b><i>" + escapeHtml(result.id) + "</i></b> posted:</p><div class='msg'> " + escapeHtml(result.message) + "</div></div>";
    }
    if (resultString == "") {
      resultString = "<i>Enter search term to see results</i>"
    }
    document.getElementById("searchResults").innerHTML = resultString;
  

  }
  xhr.open(oFormElement.method, oFormElement.action, true);
  xhr.send(new FormData(oFormElement));
  return false;
}

function escapeHtml(html) {
  return html.replace(REGEXP_LT, "&lt;").replace(REGEXP_GT, "&gt;");
}