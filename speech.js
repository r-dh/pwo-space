

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();

recognition.lang = "nl-NL";
recognition.interimResults = false;


//const loadingScreen = document.getElementById('loading-screen');

loadingScreen.addEventListener('transitionend', () => {
	const btn = document.querySelector('.button.mic')
	const intro = document.getElementById("intro")

	btn.addEventListener("click", () => {
	  recognition.start();
	  updateInfoStatus(true);
	});

});


function updateInfoStatus(listening) {
	if(listening) {
		intro.innerHTML = "Listening..."
		intro.style.display = ""
	} else {
		intro.style.display = "none"
	}
}

function updateBottomStatus(text) {
	const bottomtext = document.getElementById("instructions")
	if(text !== "") {
		bottomtext.innerHTML = text
		intro.style.display = ""
	} else {
		bottomtext.innerHTML = ""
		intro.style.display = "none"
	}
}


recognition.onresult = function (event) {
  const last = event.results.length - 1;
  const text = event.results[last][0].transcript;
  console.log(text);
  updateBottomStatus(text);
}