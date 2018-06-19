function lot_content(index) {
	var contentWindow = window.open('content/'+index+'/', "", "width=400,height=650");
}

function filterTest() {
	filterDiv = document.getElementById('af-Model');
    filterDiv.classList.toggle("show");
}