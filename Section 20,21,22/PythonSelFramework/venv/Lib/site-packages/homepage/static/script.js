function oneElementInit(a, b) {
  if (null !== document.querySelector(a))
    return new b(document.querySelector(a));
}
function initElement(elementClassName, elementInitFunction) {
  var x = document.getElementsByClassName(elementClassName);
  if (x[0] !== null){
    for(var y = 0; y < x.length; y++){
      elementInitFunction(x[y]);
    }
  }
}
function loadNewPage(pageUrl){
  window.open(pageUrl, '_blank');
}
var cdSiteTopAppBar = oneElementInit(".mdc-top-app-bar", mdc.topAppBar.MDCTopAppBar);
var downloadTextField = oneElementInit(".mdc-text-field", mdc.textField.MDCTextField);
var radio1 = oneElementInit("#radio-btn-1", mdc.radio.MDCRadio.attachTo);
var radio2 = oneElementInit("#radio-btn-2", mdc.radio.MDCRadio.attachTo);
var formField1 = oneElementInit("#form-field-1", mdc.formField.MDCFormField.attachTo);
var formField2 = oneElementInit("#form-field-2", mdc.formField.MDCFormField.attachTo);
var previousList = oneElementInit(".mdc-list", mdc.list.MDCList.attachTo);
oneElementInit("#submit-main-form", mdc.ripple.MDCRipple.attachTo);
initElement("mdc-button", mdc.ripple.MDCRipple.attachTo);
formField1.input = radio1;
formField2.input = radio2;
radio1.value = "mp3";
radio2.value = "m4a";
radio1.listen('click', () => {
  radio1.checked = true;
  radio2.checked = false;
});

radio2.listen('click', () => {
  radio2.checked = true;
  radio1.checked = false;
});

var checkbox = oneElementInit(".mdc-checkbox", mdc.checkbox.MDCCheckbox.attachTo);
var checkboxFormField = oneElementInit("#checkbox-form-field", mdc.formField.MDCFormField.attachTo);
checkboxFormField.input = checkbox;
checkbox.checked = true;

var qualityDict = {
  "Standard (128k, Fast)": 128,
  "Good (192k, Medium)": 192,
  "Best (256k, Slow)": 256
};

var siteMenu = oneElementInit("#main-quality-menu", mdc.menu.MDCMenu.attachTo);
document.getElementById("menu-opener-btn").addEventListener("click", function(evt){
    siteMenu.open = !siteMenu.open;
});
siteMenu.listen("MDCMenu:selected", function(evt){
  document.getElementById("menu-opener-btn").innerHTML = evt.detail.item.innerText;
});
oneElementInit("#menu-pref-1", mdc.ripple.MDCRipple.attachTo);
oneElementInit("#menu-pref-2", mdc.ripple.MDCRipple.attachTo);
oneElementInit("#menu-pref-3", mdc.ripple.MDCRipple.attachTo);

var mdcSnackBar = oneElementInit(".mdc-snackbar", mdc.snackbar.MDCSnackbar.attachTo);
function displayMDCSnackbar(a, b, c, d) {
  mdcSnackBar.timeoutMs = d;
  mdcSnackBar.labelText = a;
  mdcSnackBar.actionButtonText = b;
  document.getElementById("snackbarActionBtnRipple").onclick = c;
  mdcSnackBar.open();
}

function getPreviousTrack(trackPath){
  let a = document.createElement('a');
  a.href = trackPath;
  a.download = trackPath.split('/').pop();
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function sendDownloadRequest() {
  if (downloadTextField.value !== "" && downloadTextField.valid == true) {
    document.getElementsByClassName("adjusted-card-actions")[0].innerHTML = linearProgressBar;
    document.getElementById("format-selection").innerHTML = "Your track is downloading, this may take a while depending on the length of the video(s) and speed of the server.";
    document.getElementById("form-field-1").style.display = "none";
    document.getElementById("form-field-2").style.display = "none";
    document.getElementById("checkbox-control").style.display = "none";
    document.getElementById("checkbox-form-field").style.display = "none";
    document.getElementById("quality-selection").style.display = "none";
    document.getElementById("site-menu-anchor").style.display = "none";
    var XHR = new XMLHttpRequest();
    var FD  = new FormData();
    FD.append("videoURL", downloadTextField.value);

    if (radio1.checked) {
      FD.append("format_preference", "mp3");
    } else if (radio2.checked) {
      FD.append("format_preference", "m4a");
    }

    if (checkbox.checked) {
      FD.append("attach_thumb", "yes");
    } else {
      FD.append("attach_thumb", "no");
    }

    FD.append("quality_preference", qualityDict[document.getElementById("menu-opener-btn").innerHTML]);

    XHR.onreadystatechange = function(evt) {
      if (XHR.readyState == 4 && XHR.status == 200) {
        getPreviousTrack(evt.target.responseText);
        window.location.reload(false);

      } else if (XHR.readyState == 4 && XHR.status >= 300) {
        mdcSnackBar.listen("MDCSnackbar:closing", function() {
          mdcSnackBar.open();
        });
        displayMDCSnackbar("Encountered an error, refresh the page and try again.", "Refresh", function(){window.location.reload(false);}, 10000);
      }
    };
    XHR.open('POST', './');
    XHR.send(FD);
  } else {
    displayMDCSnackbar("Please ensure that the link is valid and not empty.", "OK", function(){}, 5000);
  }
}

var linearProgressBar = `
<div role="progressbar" class="mdc-linear-progress mdc-linear-progress--indeterminate">
  <div class="mdc-linear-progress__buffering-dots"></div>
  <div class="mdc-linear-progress__buffer"></div>
  <div class="mdc-linear-progress__bar mdc-linear-progress__primary-bar">
    <span class="mdc-linear-progress__bar-inner"></span>
  </div>
  <div class="mdc-linear-progress__bar mdc-linear-progress__secondary-bar">
    <span class="mdc-linear-progress__bar-inner"></span>
  </div>
</div>
`;

window.mdc.autoInit();
