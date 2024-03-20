// Use Google's public STUN server
const iceConfig = {
    'iceServers': [{'urls': ['stun:stun2.1.google.com:19302']}]
};

// create a WebRTC connection object
let webRTCConnection = new RTCPeerConnection(iceConfig);


function processMessageAsWebRTC(message, messageType) {
    switch (messageType) {
        case 'webRTC-offer':
            void webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.offer));
            webRTCConnection.createAnswer().then(answer => {
                void webRTCConnection.setLocalDescription(answer);
                socket.send(JSON.stringify({'messageType': 'webRTC-answer', 'answer': answer}));
            });
            break;
        case 'webRTC-answer':
            void webRTCConnection.setRemoteDescription(new RTCSessionDescription(message.answer));
            break;
        case 'webRTC-candidate':
            void webRTCConnection.addIceCandidate(new RTCIceCandidate(message.candidate));
            break;
        default:
            console.log("received an invalid WS messageType");
    }
}

function connectWebRTC() {
    // create and send an offer
    webRTCConnection.createOffer().then(webRTCOffer => {
        socket.send(JSON.stringify({'messageType': 'webRTC-offer', 'offer': webRTCOffer}));
        void webRTCConnection.setLocalDescription(webRTCOffer);
    });
}
