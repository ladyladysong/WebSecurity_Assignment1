/**
 * Creates a new theme chooser select component, positions it in the top right
 * corner and selects the appropriate option for the passed in theme
 */
function createThemeChooser(theme) {
  
  document.write("<select class='themeselect' id='theme' onchange='changeTheme(this)'>");
  document.write("<option value='default'");
  if (theme != "dark") {
    document.write(" selected>default</option><option value='dark'>dark</option>")
  } else {
    document.write(">default</option><option value='dark' selected>dark</option>")
  }
  document.write("<select>");

}

/**
 * Changes the current theme by setting the new theme value in the hash part
 * of the URL and reloading the page, forcing the code below to run again
 */
function changeTheme(selectElem) {
  window.location.hash = "#" + selectElem.value;
  window.location.reload();
}

/**
 * Extract the contents of the hash portion of the URL and set the value in the
 * localStorage, for later use
 */
if (window.location.hash) {
  if (localStorage.getItem("theme") != decodeURIComponent(document.location.hash).substring(1)) {
    localStorage.setItem('theme', decodeURIComponent(document.location.hash).substring(1));
    window.location.reload();
  }
}

/**
 * If a value exists in localStorage read the value and use it as the theme value
 * for the page. Having set the theme for the page, create the theme chooser
 * with the current theme selected.
 */
if (localStorage.getItem("theme")) {
  //VULN DOM Based XSS, user can inject code after # and be stored in document.write()
  /**
   *   var finalTheme = themeFilter(localStorage.getItem("theme"));
  document.write("<body class='" + finalTheme + "'>"); 
  createThemeChooser(finalTheme);
   */
  document.write("<body class='" + encodeURIComponent(localStorage.getItem("theme")) + "'>");
  createThemeChooser(localStorage.getItem("theme"));
  


} else {
  document.write("<body class='default'>");
  createThemeChooser("default");
}

function themeFilter(inputTheme){
  var after  = 'default';
  var secureFlag = true;
  if (inputTheme != 'dark' && inputTheme != 'default'){
    secureFlag = false;
  }
  const finalTheme = secureFlag? inputTheme:after;
  return finalTheme;

}