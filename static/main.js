// Get DOM elements
const typingAnimation = document.getElementById('typing-animation');
const searchField = document.querySelector('.search-field');
const infoSection = document.querySelector('.info-section');
const mapSection = document.querySelector('.map-section');
const submitButton = document.querySelector('.submit-button');
const chatMessages = document.querySelector('#chat-messages');
const saveOutput = document.querySelector('#save-output');
const saveOutputText = document.getElementById('save-output-text');
const saveOutputLoading = document.getElementById('save-output-loading');
const spinnerDiv = document.getElementById('Spinner');
const spinner1Div = document.getElementById('Spinner1');
const chatInput = document.getElementById('chatInput');
const submitBtn = document.getElementById('submitBtn');
const viewDetails = document.getElementById('viewDetails');
const history = document.getElementById("history");
const id = document.body.getAttribute('data-your-parameter');
const chatHistory = [];

//View List
window.onload = function() {
  chatInput.disabled = true;
  fetch(`/viewList?id=${id}`)
  .then(response => response.json())
  .then(data =>{
    viewList(data)
  })
  .catch(error =>{
    console.log('Error',error);
  })

}

function viewList(submissions) {
  submissions.forEach(submission => {
  const dateString = submission.createdDate;
  const date = new Date(dateString);
  const formattedDate = date.toLocaleDateString("en-US", {
  year: "numeric",
  month: "2-digit",
  day: "2-digit"
});
  const submissionDiv = document.createElement("div");
  submissionDiv.classList.add("hisor", "rounded");
  submissionDiv.textContent = submission.address + ' - Date Submitted ' + formattedDate;
  console.log(submissionDiv)
  history.appendChild(submissionDiv);
  })  
};
//Autocomplete address field
 function initialize() {
  // console.log('reached111')
  chatHistory.formattedAddress = '';
  const input = document.getElementById('fromloc');
  const autocomplete = new google.maps.places.Autocomplete(input);
  google.maps.event.addListener(autocomplete, 'place_changed', function () {
    spinnerDiv.style.display = 'flex';
    spinnerDiv.classList.remove("spinnerHidden"); // start spinning
    const place = autocomplete.getPlace();
    // console.log(place)
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
      })
      .then(response => response.json())
      .then(data => {
        // console.log(data)
        if (data.status != true) {
          spinnerDiv.classList.add('spinnerHidden');
          // spinnerDiv.style.display = 'none';
          alert(data.message)
        }
        else{
          
          spinnerDiv.classList.add('spinnerHidden'); 
          const address = data.address;
          const status = data.status;
          const price = data.price;
          const bed = data.bed;
          const bath = data.bath;
          const sizeSqft = data["size-sqft"];
          const sizeAcre = data["size-acre"];

          document.getElementById('field1').value = address;
          document.getElementById('field3').value = price;
          document.getElementById('field4').value = bed;
          document.getElementById('field5').value = bath;
          document.getElementById('field6').value = sizeSqft;
          document.getElementById('field7').value = sizeAcre;
        }
      })
      .catch(error => {
        console.error("Error:", error);
      });
      
  });
}
google.maps.event.addDomListener(window, 'load', initialize);
submitButton.addEventListener('click', async () => {
  
  const address = document.getElementById('field1').value;
  const propertyType = document.getElementById('field2').value;
  const price = document.getElementById('field3').value;
  const bed = document.getElementById('field4').value;
  const bath = document.getElementById('field5').value;
  const sizeSqft = document.getElementById('field6').value;
  const lotSize = document.getElementById('field7').value;
  const keyFeatures = document.getElementById('field13').value;
  const yearBuilt = document.getElementById('field8').value;
  const architecturalStyle = document.getElementById('field9').value; 
  const bedBathDist = document.getElementById('field10').value;
  const commName = document.getElementById('field11').value;
  const schoolDist = document.getElementById('field12').value;
  const EEASF = document.getElementById('field14').value;
  const HOA = document.getElementById('field15').value;
  const additionalComments = document.getElementById('field16').value;
  if (!address || !propertyType || !lotSize || !yearBuilt || !keyFeatures || !price || !bed || !bath || !sizeSqft) {
    alert('Please fill out all mandatory fields');
    
  }
  
  else{
  
  spinner1Div.style.display = 'flex';
  spinner1Div.classList.remove("spinnerHidden");
  const currentDate = new Date();
  const dateTime = currentDate.toLocaleString();
  chatHistory.push({
    formattedAddress: address,
    price: price,
    bed: bed,
    bath: bath,
    sizeSqft: sizeSqft,
    sizeAcre: lotSize,
    propertyType: propertyType,
    yearBuilt: yearBuilt,
    architecturalStyle: architecturalStyle,
    bedBathDist: bedBathDist,
    commName: commName,
    schoolDist: schoolDist,
    keyFeatures: keyFeatures,
    EEASF: EEASF,
    HOA: HOA,
    additionalComments: additionalComments,
    dateTime: dateTime
  })
  
  const userData = {
    'address':address,
    'price':price,
    'bed':bed,
    'bath':bath,
    'sizeSqft':sizeSqft,
    'sizeAcre':lotSize
  };

  // Clear search field
  searchField.value = '';

  // const response = await fetch(`/chatbot?user_id=${USER_ID}`, {
  const response = await fetch(`/chatbot?status=1`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });

  const data = await response.json();

  spinner1Div.classList.add('spinnerHidden');
  displayBotMessage(data.firstResponse);

  // Second Response
  spinner1Div.style.display = 'flex';
  spinner1Div.classList.remove("spinnerHidden");
  const secondresponse = await fetch(`/chatbot?status=2`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(userData)
  });

  const secondData = await secondresponse.json();
  // typingAnimation.style.display = 'none';
  spinner1Div.classList.add('spinnerHidden');
  displayBotMessage(secondData.secondResponse);
  chatInput.disabled = false;
  }
});

//Customer message
function handleCustomerMessage() {
  const message = chatInput.value;
  displayUserMessage(message);
  chatInput.value='';
  spinner1Div.style.display = 'flex';
  spinner1Div.classList.remove("spinnerHidden");
  // typingAnimation.style.display = 'block';
  const chatData = JSON.stringify(chatHistory);
  console.log(id)
  fetch(`/saveChat?status=2&id=${id}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: chatData
  })
  .then(response => response.json())

  .then(data => {
    spinner1Div.classList.add('spinnerHidden');
    displayBotMessage(data.response)
  })
  .catch(error => {
    spinner1Div.classList.add('spinnerHidden');
    console.error('Error saving chat history:', error);
  });
}

function handleCustomerMessageEvents(event) {
  if (event.type === 'keypress' && event.key === 'Enter') {
    handleCustomerMessage();
  } else if (event.type === 'click') {
    handleCustomerMessage();
  }
}
chatInput.addEventListener('keypress', handleCustomerMessageEvents);
submitBtn.addEventListener('click', handleCustomerMessageEvents);

//Save Output
saveOutput.addEventListener('click', async () =>{
  console.log(chatHistory)
  console.log('clicked')

  // Show loading sign and disable the button
  saveOutputText.style.display = 'none';
  saveOutputLoading.style.display = 'inline-block';
  saveOutput.disabled = true;

  const chatData = JSON.stringify(chatHistory);
  fetch(`/saveChat?status=1&id=${id}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: chatData
  })
  .then(response => response.json())

  .then(data => {
    saveOutputText.style.display = 'inline-block';
    saveOutputLoading.style.display = 'none';
    saveOutput.disabled = false;
    alert(data.status);
  })
  .catch(error => {
    saveOutputText.style.display = 'inline-block';
    saveOutputLoading.style.display = 'none';
    saveOutput.disabled = false;
    console.error('Error saving chat history:', error);
  });
})

// Function to display bot message
function displayBotMessage(message) {
  const container = document.createElement('div');
  container.classList.add('message-container');
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', 'bot');
  messageElement.style.borderRadius = '15px';
  const messageText = document.createElement('p');
  messageText.innerText = message;
  messageElement.appendChild(messageText);
  container.appendChild(messageElement);

  const copyButton = document.createElement('button');
  copyButton.innerText = 'Copy';
  copyButton.classList.add('reqbutton');
  copyButton.addEventListener('click', () => {
    copyToClipboard(message);
  });
  container.appendChild(copyButton);

  const conversation = document.querySelector('.conversation');
  conversation.appendChild(container);

  const currentDate = new Date();
  const dateTime = currentDate.toLocaleString();
  chatHistory.push({
    sender: 'bot',
    message: message,
    dateTime: dateTime
  });
}

// Function to display user message
function displayUserMessage(message) {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', 'user');
  const messageText = document.createElement('p');
  messageText.innerText = message;
  messageElement.appendChild(messageText);
  chatMessages.appendChild(messageElement);
  
  const conversation = document.querySelector('.conversation');
  conversation.appendChild(messageElement);

  const currentDate = new Date();
  const dateTime = currentDate.toLocaleString();
  chatHistory.push({
    sender: 'user',
    message: message,
    dateTime: dateTime
  });
}

function copyToClipboard(text) {
  const textarea = document.createElement('textarea');
  textarea.value = text;
  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand('copy');
  document.body.removeChild(textarea);
  alert('Chat content copied to clipboard!');
}


