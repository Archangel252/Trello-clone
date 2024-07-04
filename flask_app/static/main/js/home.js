var socket;

document.addEventListener('DOMContentLoaded', function() {
    var socket = io();

    var lists = document.querySelectorAll('.list');
    lists.forEach(function(list) {
        new Sortable(list, {
            group: 'shared',
            animation: 150,
            onEnd: function(event) {
                var cardId = event.item.id.split('-')[1];
                var newListId = event.to.id.split('-')[1];

                // Emit the drag-and-drop event to the server
                socket.emit('cardMoved', {
                    card_id: cardId,
                    new_list_id: newListId,
                    board_id: board_id
                });
            }
        });
    });

    // Listen for cardMoved events from the server
    socket.on('cardMoved', function(data) {
        var card = document.getElementById('card-' + data.card_id);
        var newList = document.getElementById('list-' + data.new_list_id);
        newList.appendChild(card);
    });
});
    document.addEventListener("keypress", handleKeyPress);
    $(document).ready(function(){
        
        socket = io.connect('http://' + document.domain + ':' + location.port + '/cur_board');
        //socket = io.connect('https://' + document.domain + ':' + location.port + '/chat');
        socket.on('connect', function() {
            socket.emit('joined', {'board_id' : board_id});
        });
        //  updates the states of the chat
        socket.on('status', function(data) {     
            let tag  = document.createElement("p");
            let text = document.createTextNode(data.msg);
            let element = document.getElementById("chat");
            tag.appendChild(text);
            tag.style.cssText = data.style;
            element.appendChild(tag);
            $('#chat').scrollTop($('#chat')[0].scrollHeight);
        });
        // adds chats the the chat box
        socket.on('chat', function(data) {    
            let tag  = document.createElement("p");
            let text = document.createTextNode(data.msg);
            let element = document.getElementById("chat");
            tag.appendChild(text);
            tag.style.cssText = data.style;
            element.appendChild(tag);
            $('#chat').scrollTop($('#chat')[0].scrollHeight);
        });
        socket.on('fetch_id', function(data) {
            console.log('Received data from the server:', data);
        });      
        socket.on('createCard', function(data) {
            const listElement = document.getElementById(`list-${data.id}`);
            console.log(data.card_id)
            // Create new card element
            const cardElement = document.createElement('div');
            cardId = `${data.card_id}`;
            console.log(`${data.card_id}`)
            cardElement.id = cardId
            cardElement.className = 'card';
            cardElement.innerHTML = `
                <p id="content-card-${cardId}">click EDIT to edit</p>
                <div class="button-container" id="buttons-${cardId}">
                <button onclick="editCard('${cardId}')">EDIT</button>
                <button onclick="delCard('${cardId}')">DELETE</button>
                </div>
            `;

            // Append the new card to the list
            listElement.appendChild(cardElement);

        });  
        socket.on('delete', function(data) {
            const cardElement = document.getElementById(`${data.id}`);
            console.log(`card-${data.id}`);
            console.log('deleting');
            // delete element 
            //cardElement.parentNode.removeChild(cardElement);
            cardElement.style.display = 'none';
        });  
        socket.on('edit', function(data) {
            console.log(`${data.card_id}`);
            var cardElement = document.getElementById(`content-card-${data.card_id}`);
            cardElement.innerText = data.edits;    
        });  
    });
   
    // function to exit the chat
    function LeaveChat()
    {
        socket.emit('left', {'board_id' : board_id});
        window.location.href = "/login";
    }
    // inputs the chat when enter is pressed
    function handleKeyPress(event) {
    if (event.key === "Enter") {
        let chatElement = document.getElementById('chatInput'); 
        let chatText = chatElement.value;
        socket.emit('chat', {'text' : chatText, 'board_id' : board_id});
        chatElement.value = ''        
    }
    
}
function addCard(id)
    {
        socket.emit('addcard', {'board_id' : board_id, 'list_id' : id});
    }
function delCard(id)
    {
        
        socket.emit('delcard', {'board_id' : board_id, 'card_id' : id});
    }
function editCard(card_id)
    {
        console.log('inital edit button');
        console.log('content-card-' + card_id);

        var contentP = document.getElementById('content-card-' + card_id);
        var currentText = contentP.innerText;
        var inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.value = currentText;
        inputField.id = 'edit-' + card_id;  

        
        contentP.parentNode.replaceChild(inputField, contentP);

        // Focus the input field and select the text inside it
        inputField.focus();
        inputField.select();

        var buttons = document.getElementById('buttons-' + card_id);
        buttons.style.display = 'none';

        var edits;
        inputField.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                // Create ah element
                var newP = document.createElement('p');
                newP.id = 'content-card-' + card_id;
                edits = inputField.value;
                newP.innerText = inputField.value; 
    
                // Replace the input field 
                inputField.parentNode.replaceChild(newP, inputField);
                buttons.style.display = '';
                socket.emit('editcard', {'board_id' : board_id, 'card_id' : card_id, 'edits' : edits});
            }
        });
        
    }