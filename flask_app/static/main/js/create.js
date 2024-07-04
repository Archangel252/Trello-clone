var boardId;
var newMembers = [];

document.addEventListener('DOMContentLoaded', function() {
    // Initialize socket connection
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/create');

    // Socket event listeners
    socket.on('connect', function() {
        socket.emit('joined', {});
    });

    socket.on('board_id', function(data) {
        console.log(data);
        boardId = data.id;
    });

    socket.on('redirect', function(data) {
        window.location.href = data.url;
    });

    // Event listener for the create button
    var createButton = document.getElementById('done');
    createButton.addEventListener('click', createBoard);

    // Event listener for the add member button
    var addMemberButton = document.querySelector('.members button');
    addMemberButton.addEventListener('click', addMember);
});

// Function to create a new board
function createBoard() {
    var nameInput = document.getElementById('name');
    var boardName = nameInput.value.trim();

    if (boardName === '') {
        alert('Please enter a board name');
        return;
    }

    var socket = io.connect('http://' + document.domain + ':' + location.port + '/create');
    socket.emit('createboard', { 'name': boardName, 'members': newMembers });
    window.location.href = "/boards";

    // Optionally, reset the input fields
    nameInput.value = '';
    newMembers = [];
    document.getElementById('email').value = '';
}

// Function to add a new member to the board
function addMember() {
    var memInput = document.getElementById('email');
    var email = memInput.value.trim();

    if (email === '') {
        alert('Please enter an email address');
        return;
    }

    newMembers.push(email);
    console.log("Added member:", email);

    // Optionally, update the UI to show the added members
    var memberList = document.getElementById('member-list');
    if (!memberList) {
        memberList = document.createElement('ul');
        memberList.id = 'member-list';
        document.querySelector('.members').appendChild(memberList);
    }

    var listItem = document.createElement('li');
    listItem.textContent = email;
    memberList.appendChild(listItem);

    // Clear the input field
    memInput.value = '';
}

