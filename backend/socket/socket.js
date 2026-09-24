import {Server} from 'socket.io';


let io;

export const initialize = (server) => {
    io = new Server(server, {
        cors: {
            origin: "http://localhost:5173",
        }
    });
    io.on('connection', (socket) => {
        console.log('Client connected');
        socket.on('disconnect', () => {
            console.log('Client disconnected');
        });
    });
    

}

export const getIO = () => {
    return io;
};