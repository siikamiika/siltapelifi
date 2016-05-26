#!/usr/bin/env python3
from tornado import web, ioloop
from tornado.log import enable_pretty_logging; enable_pretty_logging()
import json

class Island(object):

    id_counter = 0

    def __init__(self, x, y, degree):
        self.x = x
        self.y = y
        self.degree = degree
        self.connectables = []
        self.connections = []
        self.id = Island.id_counter
        Island.id_counter += 1

    def __repr__(self):
        return 'Island{}({}, {}, {}, [{}], ([{}]))'.format(
                self.id,
                self.x,
                self.y,
                self.degree,
                ', '.join([str(c.id) for c in self.connections]),
                ', '.join([str(c.id) for c in self.connectables]),
                )

    def serialize(self):
        return dict(
                x=self.x,
                y=self.y,
                degree=self.degree,
                connectables=[c.id for c in self.connectables],
                connections=[c.id for c in self.connections],
                id=self.id,
                )

    def add_connectable(self, island):
        self.connectables.append(island)

    def connect(self, island):
        if island not in self.connectables:
            raise Exception('cannot build a bridge here')
        if len(self.connections) == self.degree or len(island.connections) == island.degree:
            raise Exception('too many bridges connected to this island')
        self.connections.append(island)
        island.connections.append(self)
        if self.connections.count(island) == 2:
            self.connectables.remove(island)
            island.connectables.remove(self)

    def disconnect(self, island):
        if self.connections.count(island) == 2:
            self.connectables.append(island)
            island.connectables.append(self)
        self.connections.remove(island)
        island.connections.remove(self)


class Bridge(object):

    def __init__(self, i, j):
        self.i = i
        self.j = j

    def __repr__(self):
        return 'Bridge({}, {})'.format(i, j)
    
    def serialize(self):
        return dict(i=self.i, j=self.j)


class BridgesGame(object):

    def __init__(self, size_x, size_y):
        self.size_x = size_x
        self.size_y = size_y
        self.islands = []
        self.bridges = []

    def _win(self):
        for i in self.islands:
            if len(i.connections) != i.degree:
                return False
        else:
            return True

    def add_island(self, island):
        self.islands.append(island)

    def add_bridge(self, bridge):
        try:
            self.islands[bridge.i].connect(self.islands[bridge.j])
            self.bridges.append(bridge)
        except Exception as e:
            print(e)

    def remove_bridge(self):
        try:
            bridge = self.bridges[-1]
            self.islands[bridge.i].disconnect(self.islands[bridge.j])
            self.bridges.remove(bridge)
        except Exception as e:
            print(e)

    def solve_connectables(self):
        # sausage and spam
        for island in self.islands:
            # up
            for y in range(island.y+2, self.size_y):
                matches = list(filter(lambda i: i.x == island.x and i.y == y, self.islands))
                if matches:
                    island.add_connectable(matches[0])
                    break
            # down
            for y in range(island.y-2, -1, -1):
                matches = list(filter(lambda i: i.x == island.x and i.y == y, self.islands))
                if matches:
                    island.add_connectable(matches[0])
                    break
            # right
            for x in range(island.x+2, self.size_x):
                matches = list(filter(lambda i: i.y == island.y and i.x == x, self.islands))
                if matches:
                    island.add_connectable(matches[0])
                    break
            # left
            for x in range(island.x-2, -1, -1):
                matches = list(filter(lambda i: i.y == island.y and i.x == x, self.islands))
                if matches:
                    island.add_connectable(matches[0])
                    break

    def status(self):
        return dict(
                size_x=self.size_x,
                size_y=self.size_y,
                islands=[i.serialize() for i in self.islands],
                bridges=[b.serialize() for b in self.bridges],
                win=self._win(),
                )

    def solve(self):
        pass

class StatusHandler(web.RequestHandler):

    def get(self):
        self.set_header('Content-Type', 'application/json; charset=utf-8')
        self.write(json.dumps(game.status()))

class BridgeAddHandler(web.RequestHandler):

    def post(self):
        data = json.loads(self.request.body.decode('utf-8'))
        game.add_bridge(Bridge(data['i'], data['j']))

class BridgeRemoveHandler(web.RequestHandler):

    def post(self):
        game.remove_bridge()

def get_app():

    return web.Application([
        (r'/status', StatusHandler),
        (r'/addbridge', BridgeAddHandler),
        (r'/removebridge', BridgeRemoveHandler),
        (r'/(.*)', web.StaticFileHandler,
            {'path': 'client', 'default_filename': 'index.html'}),
    ])

if __name__ == '__main__':
    # autogenerated by 
    # http://www.chiark.greenend.org.uk/~sgtatham/puzzles/js/bridges.html
    game = BridgesGame(7, 7)
    game.add_island(Island(0,6,3))
    game.add_island(Island(4,6,4))
    game.add_island(Island(6,6,3))
    game.add_island(Island(1,5,2))
    game.add_island(Island(3,5,1))
    game.add_island(Island(6,4,2))
    game.add_island(Island(1,2,2))
    game.add_island(Island(4,2,6))
    game.add_island(Island(6,2,4))
    game.add_island(Island(0,1,4))
    game.add_island(Island(2,1,2))
    game.add_island(Island(4,0,3))
    game.add_island(Island(6,0,2))
    game.solve_connectables()

    app = get_app()
    app.listen(8000)
    main_loop = ioloop.IOLoop.instance()
    main_loop.start()
