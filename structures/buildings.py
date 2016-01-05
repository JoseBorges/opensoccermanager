#!/usr/bin/env python3

import data


class Buildings:
    class Building:
        def __init__(self):
            self.name = ""
            self.size = 0
            self.cost = 0
            self.number = 0
            self.filename = ""

    def __init__(self):
        self.buildings = []
        self.filenames = ("programmevendor", "stall", "burgerbar", "bar", "smallshop", "largeshop", "cafe", "restaurant")

        self.populate_data()

    def get_buildings(self):
        '''
        Return list of building names and attribute information.
        '''
        return self.buildings

    def get_building_by_index(self, index):
        '''
        Return building object for given index value.
        '''
        return self.buildings[index]

    def get_used_plots(self):
        '''
        Return number of plots currently in use.
        '''
        plots = 0

        for count, building in enumerate(self.buildings):
            plots += building.size * count

        return plots

    def populate_data(self):
        data.database.cursor.execute("SELECT * FROM buildings")

        for count, shop in enumerate(data.database.cursor.fetchall()):
            building = self.Building()
            building.name = shop[0]
            building.size = shop[1]
            building.cost = shop[2]
            building.filename = self.filenames[count]
            self.buildings.append(building)