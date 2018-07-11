class AFHolder {
  constructor(id_name) {
    this.id_name = id_name;
    this.items = [];
  }

  add(value) {
    this.items.push(value);
  }

  remove(value) {
    var index = this.items.indexOf(value);
    if (index > -1) {
      this.items.splice(index, 1);
    }
  }

  length() {
    return this.items.length;
  }

  getParameters() {
    var parametersList = [];
    for (var i = 0; i < this.items.length; i++) {
      var parameter = this.id_name + "=" + this.items[i];
      parametersList.push(parameter);
    }
    return parametersList.join("&");
  }

  debug() {
    console.log(this.id_name);
    console.log(this.items);
  }
}

class AFManager {
  constructor() {
    this.filter_list = [];
    this.possible_fieldnames = [];
  }

  process_collection_of_filters(af_div_id) {
    var afSelections = document.getElementById(af_div_id).getElementsByClassName("af-selection");
    for (var i = 0; i<afSelections.length; i++) {
      var afSelection = afSelections[i];
      var title = afSelection.getElementsByClassName("af-chkbxtitle")[0];
      var checkbox = afSelection.getElementsByTagName("input")[0];
      if (checkbox.checked) {
        this.add_filter(afSelection.parentElement.id, title.innerText.trim());
      }
    }
  }

  set_possible_fieldnames() {
    var afDivs = document.getElementsByClassName("autofilter");
    for (var i=0; i<afDivs.length; i++) {
      var fieldname = afDivs[i].getElementsByClassName("af-body")[0];
      this.possible_fieldnames.push(fieldname.id);
    }
  }

  add_filter(filter_name, value) {
    var found = false;
    for (var i=0; i<this.filter_list.length; i++) {
      if(this.filter_list[i].id_name == filter_name) {
        found = true;
        this.filter_list[i].add(value);
        break;
      }
    }
    if(!found){
      var filter = new AFHolder(filter_name);
      filter.add(value);
      this.filter_list.push(filter);
    }
  }

  remove_filter(filter_name, value) {
    for (var i=0; i<this.filter_list.length; i++) {
      if(this.filter_list[i].id_name == filter_name) {
        this.filter_list[i].remove(value);
        if(this.filter_list[i].length()==0){
          this.filter_list.splice(i, 1);
        }
        break;
      }
    }
  }

  showFilterButton() {
    var filterButton = document.getElementById("filter");
    if (this.filter_list.length > 0) {
        filterButton.style.display = "inline-block";
    } else {
        filterButton.style.display = "none";
    }
  }

  formNewUrlWithAFURLaddon(url) {
    var splittedArray = url.split("?");
    var mainURL = splittedArray[0];
    var attributesString = splittedArray[1];
    if (attributesString == null) {
    	console.log('No attributes');
    	return mainURL + '?' + this.getAFURLaddon();
    }
    else {
	    console.log(mainURL);
	    console.log(attributesString);
	    var attributes = attributesString.split("&");
	    console.log(attributes);
	    for (var i = attributes.length -1; i > -1; i--) {
	    	console.log("Attribute: " + attributes[i]);
	      	for (var j = 0; j < this.possible_fieldnames.length; j++) {
	        	console.log("Fieldname: " + this.possible_fieldnames[j]);
	        	if ( attributes[i].includes(this.possible_fieldnames[j])) {
	          		console.log("Removing");
	          		attributes.splice(i, 1)
	          		break;
	        	}
	      	}
	    }
	    console.log(attributes);
	    console.log(this.getAFURLaddon());
	    return mainURL + "?"+ attributes.join("&") +"&" + this.getAFURLaddon();	
    }
  }

  getAFURLaddon() {
    var parametersList = [];
    for (var i = 0; i < this.filter_list.length; i++) {
      parametersList.push(this.filter_list[i].getParameters());
    }
    return parametersList.join("&");
  }

  debug() {
    for (var i=0; i<this.filter_list.length; i++){
      this.filter_list[i].debug();
    }
    console.log("________________________________________");
  }
}

var afmanager = new AFManager();

window.onload = function() {load()}

function load() {
  collectSelectedAF();
}

function collectSelectedAF() {
  filterDivs = document.getElementsByClassName("autofilter");
  for (var i = 0; i < filterDivs.length; i++ ){
    afmanager.process_collection_of_filters(filterDivs[i].id);
  }
  afmanager.set_possible_fieldnames();
}

function lot_content(index) {
	var contentWindow = window.open('content/'+index+'/', "", "width=400,height=650");
}

function autoFilterMenu(filterDivId){
    filterDiv = document.getElementById(filterDivId);
    filterDiv.classList.toggle("show");
}

function afSelect(checkbox) {
  parent = checkbox.parentElement;
  grandparent = parent.parentElement;
  child = grandparent.childNodes[3];
  text = child.innerText;
  grandgrandparent = grandparent.parentElement;
  id = grandgrandparent.id;
  if (checkbox.checked){
      afmanager.add_filter(id, text);
  } else {
      afmanager.remove_filter(id, text);
  }
}

function afSelectAll(checkbox ,filterDivId) {
  filterDiv = document.getElementById(filterDivId);
  filterCheckboxes = filterDiv.getElementsByTagName("input");
  for (var i =0; i < filterCheckboxes.length; i++) {
    style = filterCheckboxes[i].parentElement.parentElement.style.display
    if (filterCheckboxes[i].checked != checkbox.checked && style !== "none")
      filterCheckboxes[i].click();
  }
}

function filterKeywordChange(inputbox, workingDivId) {
  keyword = inputbox.value.toUpperCase();
  workingDiv = document.getElementById(workingDivId);
  selectionDivs = workingDiv.getElementsByClassName("af-selection");
  for (var i =0; i<selectionDivs.length; i++) {
    selectionDiv = selectionDivs[i];
    divs = selectionDiv.childNodes;
    chkbxTitleDiv = selectionDiv.childNodes[3];
    chkbxTitle = chkbxTitleDiv.innerText.toUpperCase();
    if (chkbxTitle.includes(keyword)) {
      selectionDivs[i].style.display = "block";
    } else {
      selectionDivs[i].style.display = "none";
    }
  }
}

function applyAFs() {
  newURL = afmanager.formNewUrlWithAFURLaddon(location.href);
  loadPage(newURL);
}

function editHdd(index, URLremovalToken) {
	URLtoWorkWith = location.href.slice(0, -1);
	parts = URLtoWorkWith.split('/');
	for (var i =0; i<URLremovalToken; i++) {
		parts.pop();
	}
	var editHddWindow = window.open(parts.join('/') + '/hdd_edit/'+index+'/', "", "width=400,height=650");
}

function importNewLot(URLremovalToken) {
	URLtoWorkWith = location.href;
	parts = URLtoWorkWith.split('/');
	for (var i =0; i<URLremovalToken; i++) {
		parts.pop();
	}
	var importTarWindow = window.open(parts.join('/') + '/tar/', "", "width=360,height=100");
}

function loadPage(newURL) {
  window.location = newURL;
}

function isNumber(event) {
	keycode = event.keyCode;
	return (keycode=>48 && keycode<=57);
}

function deleteHddFromHddEdit(index) {
	if (confirm('Do you really want to delete this hdd?')) {
		URLtoWorkWith = location.href;
		URLtoWorkWith = URLtoWorkWith.replace('/hdd_edit/', '/hdd_delete/');
		loadPage(URLtoWorkWith);
	}
}