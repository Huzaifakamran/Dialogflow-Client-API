// Get DOM elements
const searchField = document.querySelector('.search-field');
const infoSection = document.querySelector('.info-section');
const mapSection = document.querySelector('.map-section');
const submitButton = document.querySelector('.submit-button');
const chatMessages = document.querySelector('#chat-messages');

//Autocomplete address field
 function initialize() {
  console.log('reached111')
  const input = document.getElementById('fromloc');
  const autocomplete = new google.maps.places.Autocomplete(input);
  google.maps.event.addListener(autocomplete, 'place_changed', function () {
    const place = autocomplete.getPlace();
    const data = {address:place};
      // document.getElementById('city2').value = place.name;
      // document.getElementById('cityLat').value = place.geometry.location.lat();
      // document.getElementById('cityLng').value = place.geometry.location.lng();
      fetch(`/address`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      }).then(response =>{
        console.log(response)
      }).catch(error =>{
        console.log("error: ",error);
      })
  });
}
google.maps.event.addDomListener(window, 'load', initialize);


// Event listener for submit button click
submitButton.addEventListener('click', async () => {
  console.log('Clicked')
  // Get user message
  const userMessage = searchField.value;

  // Clear search field
  searchField.value = '';

  // Display user message
  displayUserMessage(userMessage);
  const USER_ID = '123'
  // Send user message to server
  const response = await fetch(`/chatbot?user_id=${USER_ID}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: userMessage })
  });
  // Get response from server
  const data = await response.json();

  // Display bot response
  const botMessage = data.message;
  displayBotMessage(botMessage);
});

// Function to display bot message
function displayBotMessage(message) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', 'bot');
  const messageText = document.createElement('p');
  messageText.innerText = message;
  messageElement.appendChild(messageText);
  chatMessages.appendChild(messageElement);
}

// Function to display user message
function displayUserMessage(message) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', 'user');
  const messageText = document.createElement('p');
  messageText.innerText = message;
  messageElement.appendChild(messageText);
  chatMessages.appendChild(messageElement);
}
