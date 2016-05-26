var gameArea = document.getElementById('game');
var gameStatus = {};
var addingBridge = false;
var islandClickCache;

// xhr
var XHR = function(type, path, data, onready, async) {
    if (!onready) {onready = function(){}}
    if (!(async === false)) {async = true};
    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status == 200) {
            onready(xhr.responseText);
        }
    }

    xhr.open(type, path, async);
    xhr.send(data);
}

function updateGame() {
    XHR('GET', '/status', null, function(data) {
        gameArea.innerHTML = '';
        data = JSON.parse(data);
        gameStatus = data;
        gameStatus.grid = [];

        for (var i = 0; i < gameStatus.size_y; i++) {
            insertRow(i);
        }

        function insertRow(index_y) {
            gameStatus.grid[index_y] = [];
            var row = gameArea.insertRow(0);
            for (var i = 0; i < gameStatus.size_x; i++) {
                insertCell(row, i, index_y);
            }
        }

        function insertCell(row, index_x, index_y) {
            var cell = row.insertCell(index_x);
            gameStatus.grid[index_y][index_x] = cell;
        }

        for (var i = 0; i < gameStatus.islands.length; i++) {
            drawIsland(gameStatus.islands[i]);
        }

        function drawIsland(island) {
            var cell = gameStatus.grid[island.y][island.x];
            cell.onclick = clickIsland(island.id);
            cell.innerHTML = island.degree;
        }

        for (var i = 0; i < gameStatus.bridges.length; i++) {
            drawBridge(gameStatus.bridges[i]);
        }

        function drawBridge(bridge) {
            var start = gameStatus.islands[bridge.i];
            var end = gameStatus.islands[bridge.j];
            if (start.x == end.x) {
                for (var i = Math.min(start.y, end.y) + 1; i < Math.max(start.y, end.y); i++) {
                    addBridge(gameStatus.grid[i][start.x], '|');
                }
            } else {
                for (var i = Math.min(start.x, end.x) + 1; i < Math.max(start.x, end.x); i++) {
                    addBridge(gameStatus.grid[start.y][i], '–');
                }
            }
        }

        function addBridge(cell, chr) {
            if (cell.innerHTML == '') {
                    cell.innerHTML = chr;
            } else {
                if (chr == '–')
                    cell.innerHTML = '=';
                else
                    cell.innerHTML = '||'
            }
        }

        if (gameStatus.win) {
            alert('you win');
        }

    });

}

function clickIsland(id)  {
    return function(e) {
        if (!addingBridge) {
            addingBridge = true;
            islandClickCache = id;
        } else {
            addingBridge = false;
            var bridge = {i: islandClickCache, j: id};
            XHR('POST', '/addbridge', JSON.stringify(bridge), function(data) {
                updateGame();
            });
        }
    }
}

function removeBridge() {
    XHR('POST', '/removebridge', null, function(data) {
        updateGame();
    });
}

updateGame();
