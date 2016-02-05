#!/usr/bin/env python3

#  This file is part of OpenSoccerManager.
#
#  OpenSoccerManager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by the
#  Free Software Foundation, either version 3 of the License, or (at your
#  option) any later version.
#
#  OpenSoccerManager is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#  or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  OpenSoccerManager.  If not, see <http://www.gnu.org/licenses/>.


from gi.repository import Gtk
from gi.repository import Gdk

import data
import structures.skills
import uigtk.widgets


class Shortlist(Gtk.Grid):
    __name__ = "shortlist"

    treeselection = None

    def __init__(self):
        self.liststore = Gtk.ListStore(int, str, int, str, str, str, str, str,
                                       int, int, int, int, int, int, int, int,
                                       int)

        Gtk.Grid.__init__(self)
        self.set_row_spacing(5)

        scrolledwindow = uigtk.widgets.ScrolledWindow()
        self.attach(scrolledwindow, 0, 0, 1, 1)

        self.treeview = uigtk.widgets.TreeView()
        self.treeview.set_vexpand(True)
        self.treeview.set_hexpand(True)
        self.treeview.set_model(self.liststore)
        self.treeview.connect("row-activated", self.on_row_activated)
        self.treeview.connect("button-release-event", self.on_button_release_event)
        self.treeview.connect("key-press-event", self.on_key_press_event)
        self.treeview.treeselection.connect("changed", self.on_treeselection_changed)
        scrolledwindow.add(self.treeview)

        Shortlist.treeselection = self.treeview.get_selection()

        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Name", column=1)
        treeviewcolumn.set_expand(True)
        self.treeview.append_column(treeviewcolumn)
        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Age", column=2)
        self.treeview.append_column(treeviewcolumn)
        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Position", column=3)
        self.treeview.append_column(treeviewcolumn)
        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Club", column=4)
        self.treeview.append_column(treeviewcolumn)
        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Nationality", column=5)
        self.treeview.append_column(treeviewcolumn)
        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Value", column=6)
        self.treeview.append_column(treeviewcolumn)
        treeviewcolumn = uigtk.widgets.TreeViewColumn(title="Wage", column=7)
        self.treeview.append_column(treeviewcolumn)

        skills = structures.skills.Skills()

        for count, skill in enumerate(skills.get_skills(), start=8):
            label = Gtk.Label(skill[0])
            label.set_tooltip_text(skill[1])
            label.show()
            treeviewcolumn = uigtk.widgets.TreeViewColumn(column=count)
            treeviewcolumn.set_widget(label)
            self.treeview.append_column(treeviewcolumn)

        buttonbox = uigtk.widgets.ButtonBox()
        buttonbox.set_layout(Gtk.ButtonBoxStyle.END)
        self.attach(buttonbox, 0, 1, 1, 1)

        self.buttonPurchase = uigtk.widgets.Button("_Purchase")
        self.buttonPurchase.set_sensitive(False)
        self.buttonPurchase.set_tooltip_text("Approach owning club to request purchase.")
        self.buttonPurchase.connect("clicked", self.on_purchase_clicked)
        buttonbox.add(self.buttonPurchase)
        self.buttonLoan = uigtk.widgets.Button("_Loan")
        self.buttonLoan.set_sensitive(False)
        self.buttonLoan.set_tooltip_text("Approach owning club to request loan.")
        self.buttonLoan.connect("clicked", self.on_loan_clicked)
        buttonbox.add(self.buttonLoan)
        self.buttonRemove = uigtk.widgets.Button("_Remove")
        self.buttonRemove.set_sensitive(False)
        self.buttonRemove.set_tooltip_text("Remove the player from the shortlist.")
        self.buttonRemove.connect("clicked", self.on_remove_clicked)
        buttonbox.add(self.buttonRemove)
        self.buttonScout = uigtk.widgets.Button("_Scout Report")
        self.buttonScout.set_sensitive(False)
        self.buttonScout.set_tooltip_text("Request report from scouting team on player.")
        self.buttonScout.connect("clicked", self.on_scout_report_clicked)
        buttonbox.add(self.buttonScout)

        self.contextmenu = ContextMenu()

    def on_treeselection_changed(self, treeselection):
        '''
        Update interface buttons for selection.
        '''
        model, treeiter = treeselection.get_selected()

        if treeiter:
            self.buttonPurchase.set_sensitive(True)
            self.buttonLoan.set_sensitive(True)
            self.buttonRemove.set_sensitive(True)

            if self.club.scouts.get_staff_count() > 0:
                self.buttonScout.set_sensitive(True)
        else:
            self.buttonPurchase.set_sensitive(False)
            self.buttonLoan.set_sensitive(False)
            self.buttonRemove.set_sensitive(False)
            self.buttonScout.set_sensitive(False)

    def on_row_activated(self, treeview, treepath, treeviewcolumn):
        '''
        View player information screen for activated player.
        '''
        model = treeview.get_model()
        playerid = model[treepath][0]

        data.window.screen.change_visible_screen("playerinformation")
        data.window.screen.active.set_visible_player(playerid)

    def on_purchase_clicked(self, *args):
        '''
        Confirm purchase approach for player and setup negotiation.
        '''
        model, treeiter = self.treeview.treeselection.get_selected()
        playerid = model[treeiter][0]

        data.negotiations.initialise_purchase(playerid)

    def on_loan_clicked(self, *args):
        '''
        Confirm loan approach for player and setup negotiation.
        '''
        model, treeiter = self.treeview.treeselection.get_selected()
        playerid = model[treeiter][0]

        data.negotiations.initialise_loan(playerid)

    def on_remove_clicked(self, *args):
        '''
        Ask to remove selected player from shortlist.
        '''
        model, treeiter = self.treeview.treeselection.get_selected()
        playerid = model[treeiter][0]

        dialog = RemoveShortlist()

        if dialog.show(playerid) == 1:
            self.club.shortlist.remove_from_shortlist(playerid)

            self.populate_data()

    def on_scout_report_clicked(self, *args):
        '''
        Provide a scout report for the selected player.
        '''
        model, treeiter = self.treeview.treeselection.get_selected()
        playerid = model[treeiter][0]

        ScoutReport()

    def on_key_press_event(self, widget, event):
        if Gdk.keyval_name(event.keyval) == "Menu":
            event.button = 3
            self.on_context_menu_event(event)

    def on_button_release_event(self, widget, event):
        if event.button == 3:
            self.on_context_menu_event(event)

    def on_context_menu_event(self, event):
        model, treeiter = Shortlist.treeselection.get_selected()

        if treeiter:
            playerid = model[treeiter][0]

            self.contextmenu.playerid = playerid
            self.contextmenu.show()
            self.contextmenu.popup(None,
                                   None,
                                   None,
                                   None,
                                   event.button,
                                   event.time)

    def populate_data(self):
        self.liststore.clear()

        for playerid in self.club.shortlist.get_shortlist():
            player = data.players.get_player_by_id(playerid)

            self.liststore.append([playerid,
                                   player.get_name(),
                                   player.get_age(),
                                   player.position,
                                   player.get_club_name(),
                                   player.get_nationality_name(),
                                   player.value.get_value_as_string(),
                                   player.wage.get_wage_as_string(),
                                   player.keeping,
                                   player.tackling,
                                   player.passing,
                                   player.shooting,
                                   player.heading,
                                   player.pace,
                                   player.stamina,
                                   player.ball_control,
                                   player.set_pieces])

    def run(self):
        self.club = data.clubs.get_club_by_id(data.user.team)
        self.populate_data()

        self.show_all()


class ContextMenu(Gtk.Menu):
    def __init__(self):
        Gtk.Menu.__init__(self)

        menuitem = uigtk.widgets.MenuItem("Approach for _Purchase")
        menuitem.connect("activate", self.on_purchase_clicked)
        self.append(menuitem)
        menuitem = uigtk.widgets.MenuItem("Approach for _Loan")
        menuitem.connect("activate", self.on_loan_clicked)
        self.append(menuitem)
        menuitem = uigtk.widgets.MenuItem("_Remove Player")
        menuitem.connect("activate", self.on_remove_clicked)
        self.append(menuitem)
        self.menuitemScoutReport = uigtk.widgets.MenuItem("_Scout Report")
        self.menuitemScoutReport.set_sensitive(False)
        self.menuitemScoutReport.connect("activate", self.on_scout_report_clicked)
        self.append(self.menuitemScoutReport)

    def on_purchase_clicked(self, *args):
        '''
        Confirm purchase approach for player and setup negotiation.
        '''
        model, treeiter = Shortlist.treeselection.get_selected()
        playerid = model[treeiter][0]

        data.negotiations.initialise_purchase(playerid)

    def on_loan_clicked(self, *args):
        '''
        Confirm loan approach for player and setup negotiation.
        '''
        model, treeiter = Shortlist.treeselection.get_selected()
        playerid = model[treeiter][0]

        data.negotiations.initialise_loan(playerid)

    def on_remove_clicked(self, *args):
        '''
        Ask to remove selected player from shortlist.
        '''
        model, treeiter = Shortlist.treeselection.get_selected()
        playerid = model[treeiter][0]

        dialog = RemoveShortlist()

        if dialog.show(playerid) == 1:
            self.club.shortlist.remove_from_shortlist(playerid)

    def on_scout_report_clicked(self, *args):
        '''
        Provide a scout report for the selected player.
        '''
        model, treeiter = Shortlist.treeselection.get_selected()
        playerid = model[treeiter][0]

        ScoutReport()

    def show(self):
        self.club = data.clubs.get_club_by_id(data.user.team)

        self.show_all()

        sensitive = self.club.scouts.get_staff_count() > 0
        self.menuitemScoutReport.set_sensitive(sensitive)


class RemoveShortlist(Gtk.MessageDialog):
    '''
    Message dialog displayed when user attempts to remove player from shortlist.
    '''
    def __init__(self):
        Gtk.MessageDialog.__init__(self)
        self.set_transient_for(data.window)
        self.set_title("Remove From Shortlist")
        self.set_property("message-type", Gtk.MessageType.QUESTION)
        self.format_secondary_text("Removal will not cancel any ongoing transfer negotiations.")
        self.add_button("_Do Not Remove", Gtk.ResponseType.CANCEL)
        self.add_button("_Remove", Gtk.ResponseType.OK)
        self.set_default_response(Gtk.ResponseType.CANCEL)

    def show(self, playerid):
        player = data.players.get_player_by_id(playerid)
        name = player.get_name(mode=1)

        self.set_markup("<span size='12000'><b>Remove %s from shortlist?</b></span>" % (name))

        state = 0

        if self.run() == Gtk.ResponseType.OK:
            state = 1

        self.destroy()

        return state


class ScoutReport(Gtk.MessageDialog):
    '''
    Message dialog reporting on the quality of the selected player.
    '''
    def __init__(self):
        Gtk.MessageDialog.__init__(self)
        self.set_transient_for(data.window)
        self.set_modal(True)
        self.set_resizable(False)
        self.set_title("Scout Report")
        self.add_button("_Close", Gtk.ResponseType.CLOSE)
        self.connect("response", self.on_response)

        self.show()

    def on_response(self, *args):
        self.destroy()
