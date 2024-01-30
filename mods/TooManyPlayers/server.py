import sys, aerics, random, pickle, time, threading, multiprocessing

chunkSize = (16, 256, 16)

def setup(globals):
    chunks = {}

    for x in range(2):
        for z in range(2):
            chunkPosition = (x - 1, 0, z - 1)
            chunks[chunkPosition] = {}

            for i in range(int(chunkSize[0])):
                for j in range(int(chunkSize[1])):
                    for k in range(int(chunkSize[2])):
                        if j == 15:
                            blockNumber = random.choices([0, 15, 10, 18, 19, 3, 4, 16], [20, 1, 1, 2, 1, 5, 2, 1])[0]
                            chunks[chunkPosition][i, j, k] = blockNumber
                            if blockNumber == 4: chunks[chunkPosition][i, j + 1, k] = 5
                        elif j == 14: chunks[chunkPosition][i, j, k] = 2
                        elif j > 10 and j < 15: chunks[chunkPosition][i, j, k] = 6
                        elif j < 15: chunks[chunkPosition][i, j, k] = 7

    globals["world"] = chunks
    globals["worldData"] = pickle.dumps(globals["world"])
    globals["worldSize"] = len(globals["worldData"])
    globals["lastTime"] = time.time()
    globals["time"] = 0
    globals["daylight"] = 0
    globals["incrementer"] = 0

def on_connection(connection, address, id, clients, globals):
    print(f"client connected, id: {id}.")
    return {"name": "Unknown", "position": (0.0, 0.0, 0.0), "velocity": (0.0, 0.0, 0.0), "yaw": 0.0, "pitch": 0.0, "remainingWorldSize": globals["worldSize"], "chat": []}

def on_disconnection(connection, address, id, clients, globals):
    print(f"client disconnected, id: {id}.")

def on_recv(connection, address, id, clients, globals, data):
    match data[0]:
        case "getId":
            return id
        
        case "getPlayers":
            return clients
        
        case "getTime":
            currentTime = time.time()
            deltaTime = currentTime - globals["lastTime"]
            globals["lastTime"] = currentTime
            if deltaTime > 1.0: return (globals["time"], globals["daylight"])
            globals["time"] += 1 * deltaTime * 150

            if globals["incrementer"] == -1:
                if globals["daylight"] < 480:
                    globals["incrementer"] = 0
                    
            elif globals["incrementer"] == 1:
                if globals["daylight"] >= 1800:
                    globals["incrementer"] = 0

            if int(globals["time"]) % 36000 > -100 and int(globals["time"]) % 36000 < 100:
                globals["incrementer"] = 1

            elif int(globals["time"]) % 36000 > 17000 and int(globals["time"]) % 36000 < 19000:
                globals["incrementer"] = -1

            globals["daylight"] += globals["incrementer"] * deltaTime * 30
            return (globals["time"], globals["daylight"])
        
        case "getWorldSize":
            return globals["worldSize"]
        
        case "getWorldData":
            if clients[id]["remainingWorldSize"] == 0: return "finished"
            start = globals["worldSize"] - clients[id]["remainingWorldSize"]
            end = start + 1024
            if end > globals["worldSize"]: end = globals["worldSize"]
            data = globals["worldData"][start:end]
            clients[id]["remainingWorldSize"] -= len(data)
            return data
        
        case "sendMessage":
            for client in clients:
                clients[client]["chat"].append((clients[id]["name"], data[1]))

            return True
        
        case "pollMessages":
            if len(clients[id]["chat"]) == 0: return (None, None)
            return clients[id]["chat"].pop()

        case "setName":
            clients[id]["name"] = data[1]
            return True

        case "updatePlayer":
            clients[id]["position"], clients[id]["velocity"], clients[id]["yaw"], clients[id]["pitch"] = data[1:]
            return True

def main(argv):
    server = aerics.Server("localhost", 5656, recv_size = 2048)
    server.event(setup)
    server.event(on_connection)
    server.event(on_disconnection)
    server.event(on_recv)
    server.listen()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))