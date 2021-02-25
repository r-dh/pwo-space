const btn = document.querySelector('.button.mic')
const texttop = document.getElementById("texttop")
const instructions = document.getElementById("instructions")
const audio = document.getElementById("audio")

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
	btn.classList.remove("pulse");
	btn.style.display = "none";
});

function replyKey(e) {
	//If space or enter
	if(e.keyCode === 13 || e.keyCode == 32) {
		btn.click();
	}
}
document.addEventListener('keydown', replyKey);


recognition.onresult = function (event) {
	const last = event.results.length - 1;
	const text = event.results[last][0].transcript;
	console.log("Recognised: " + text);
	updateBottomStatus(text);
	//Delete input after three seconds
	setTimeout( function() { updateBottomStatus(); }, 3000);
	answer(text);

}

recognition.onend = function (event) {
	updateInfoStatus(false)
	btn.style.display = ""
}

function answer(input) {
	response(input);
}


const response = async function(input){
	let inputDict = {
	  'user_input': input
	};

	let response = await fetch('/process', {
		  method: 'POST',
		  headers: new Headers({
		    'Content-Type': 'application/json;charset=utf-8'
		  }),
		 	// body: JSON.stringify(user)
		 	body : JSON.stringify(inputDict)//{"user_input" : input}
		})
		.then(function(res) {
             if (!res.ok) throw Error(res.statusText)
             return res.blob()
		}).then(function(blob) {
			audio.src = URL.createObjectURL(blob)
			audio.play()
		  })
		  .catch(function(error) {
		    console.log("Fetch error: " + error);
		});
}
