const form = document.getElementById('form');
var labels = document.querySelectorAll("#label")

form.addEventListener('submit', e => {
     if(checkInputs()==false){
        e.preventDefault();
     }else{
     return true
     }


});


function checkInputs() {
	// trim to remove the whitespaces
	var i;
    flag = true;
	for(i=0;i<labels.length;i++){
    const labelValue = labels[i].value.trim();

	if(labelValue === '') {
		setErrorFor(label[i], '标签不能为空');
        flag = false
	} else {
		setSuccessFor(label[i]);
	}


    }
    return flag;

}

function setErrorFor(input, message) {
	const formControl = input.parentElement;
	const small = formControl.querySelector('small');
	formControl.className = 'form-group error';
	small.innerText = message;
}

function setSuccessFor(input) {
	const formControl = input.parentElement;
	formControl.className = 'form-group success';
}

