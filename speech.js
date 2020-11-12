const btn = document.querySelector('.button.mic')
const texttop = document.getElementById("texttop")
const instructions = document.getElementById("instructions")

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();

recognition.lang = "nl-NL";
recognition.interimResults = false;


function updateInfoStatus(listening) {
	if(listening) {
		texttop.innerHTML = "Aan het luisteren..."
		texttop.style.display = ""
	} else {
		texttop.style.display = "none"
	}
}

function updateBottomStatus(text) {
	if(text) {
		instructions.innerHTML = "U: " + text
		instructions.style.display = ""
	} else {
		instructions.innerHTML = ""
		instructions.style.display = "none"
	}
}

btn.addEventListener("click", () => {
	playanimation = false;
	recognition.start();
	updateInfoStatus(true);
	updateBottomStatus();
	btn.classList.remove("pulse")
	btn.style.display = "none"
});

recognition.onresult = function (event) {
	const last = event.results.length - 1;
	const text = event.results[last][0].transcript;
	console.log("Recognised: " + text);
	updateBottomStatus(text);
	//Delete input after three seconds
	setTimeout( function() { updateBottomStatus(); }, 3000);
	answer(text);
	//send to SPACE backend
}

recognition.onend = function (event) {
	updateInfoStatus(false)
	btn.style.display = ""
}

function answer(input) {
	//play audio if input contains "hello"
	if (input.includes("Hallo") || input.includes("hallo")) {
		//play audio
		//experiment with howlerjs?
		var audio = new Audio('./audio/int_voorstellen.wav');
		audio.play();
	} else {
		console.log("No hallo found")
	}
/*	$.ajax({
		url: '/process',
		data: {"user_input" : $.trim(userText)},
		type: 'POST',
		success: function(response) {
			//
		},
		error: function(error){
			console.log(error);
		}
	});*/
}
