$(document).ready(function() {
    // Connect to the WebSocket server via Socket.IO
    socket = io.connect('http://' + document.domain + ':' + location.port + '/boards');

    socket.on('connect', function() {
        socket.emit('joined', {});
    });
    socket.on('redirect', function(data) {
        // Redirect to the URL provided by the server
        window.location.href = data.url;
    });
});

function selectBoard(id){
    socket.emit('selectboard', {'id' : id});
    
}