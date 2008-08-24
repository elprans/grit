#!/usr/bin/python2.4
# Copyright (c) 2006-2008 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

''' Toolbar postprocessing class. Modifies the previously processed GRD tree
by creating separate message groups for each of the IDS_COMMAND macros.
Also adds some identifiers nodes to declare specific ids to be included
in the generated grh file.
'''

import sys
import re
import postprocess_interface
import grit.node.empty
from grit.node import misc

class ToolbarPostProcessor(postprocess_interface.PostProcessor):
  ''' Defines message groups within the grd file for each of the
  IDS_COMMAND stuff.
  '''

  _IDS_COMMAND = re.compile(r'IDS_COMMAND_')
  _GRAB_PARAMETERS = re.compile(r'(IDS_COMMAND_[a-zA-Z0-9]+)_([a-zA-z0-9]+)')

  def Process(self, rctext, rcpath, grdnode):
    ''' Processes the data in rctext and grdnode.
    Args:
      rctext: string containing the contents of the RC file being processed.
      rcpath: the path used to access the file.
      grdnode: the root node of the grd xml data generated by 
      the rc2grd tool.
    
    Return:
      The root node of the processed GRD tree.
    '''

    release = grdnode.children[2]
    messages = release.children[2]
    
    identifiers = grit.node.empty.IdentifiersNode()
    identifiers.StartParsing('identifiers', release)
    identifiers.EndParsing()
    release.AddChild(identifiers)


    #
    # Turn the IDS_COMMAND messages into separate message groups
    # with ids that are offsetted to the message group's first id
    #
    previous_name_attr = ''
    previous_prefix = ''
    previous_node = ''
    new_messages_node = self.ConstructNewMessages(release)
    for node in messages.children[:]:
      name_attr = node.attrs['name']
      if self._IDS_COMMAND.search(name_attr):
        mo = self._GRAB_PARAMETERS.search(name_attr)
        mp = self._GRAB_PARAMETERS.search(previous_name_attr)
        if mo and mp:
          prefix = mo.group(1)
          previous_prefix = mp.group(1)
          new_message_id = mp.group(2)
          if prefix == previous_prefix:
            messages.RemoveChild(previous_name_attr)
            previous_node.attrs['offset'] = 'PCI_' + new_message_id
            del previous_node.attrs['name']
            new_messages_node.AddChild(previous_node)
          else:
            messages.RemoveChild(previous_name_attr)
            previous_node.attrs['offset'] = 'PCI_' + new_message_id
            del previous_node.attrs['name']
            new_messages_node.AddChild(previous_node)
            new_messages_node.attrs['first_id'] = previous_prefix
            new_messages_node = self.ConstructNewMessages(release)
        else:
          if self._IDS_COMMAND.search(previous_name_attr):
            messages.RemoveChild(previous_name_attr)
            previous_prefix = mp.group(1)
            new_message_id = mp.group(2)
            previous_node.attrs['offset'] = 'PCI_' + new_message_id
            del previous_node.attrs['name']
            new_messages_node.AddChild(previous_node)
            new_messages_node.attrs['first_id'] = previous_prefix
            new_messages_node = self.ConstructNewMessages(release)
      else:
        if self._IDS_COMMAND.search(previous_name_attr):
          messages.RemoveChild(previous_name_attr)
          mp = self._GRAB_PARAMETERS.search(previous_name_attr)
          previous_prefix = mp.group(1)
          new_message_id = mp.group(2)
          previous_node.attrs['offset'] = 'PCI_' + new_message_id
          del previous_node.attrs['name']
          new_messages_node.AddChild(previous_node)
          new_messages_node.attrs['first_id'] = previous_prefix
          new_messages_node = self.ConstructNewMessages(release)
      previous_name_attr = name_attr
      previous_node = node

    
    self.AddIdentifiers(rctext, identifiers) 
    return grdnode

  def ConstructNewMessages(self, parent):
    new_node = grit.node.empty.MessagesNode()
    new_node.StartParsing('messages', parent)
    new_node.EndParsing()
    parent.AddChild(new_node)
    return new_node

  def AddIdentifiers(self, rctext, node):
    node.AddChild(misc.IdentifierNode.Construct(node, 'IDS_COMMAND_gcFirst', '12000', ''))
    node.AddChild(misc.IdentifierNode.Construct(node,
                                                'IDS_COMMAND_PCI_SPACE', '16', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_BUTTON', '0', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_MENU', '1', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_TIP', '2', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_OPTIONS_TEXT', '3', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_TIP_DISABLED', '4', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_TIP_MENU', '5', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_TIP_MENU_DISABLED', '6', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_TIP_OPTIONS', '7', ''))
    node.AddChild(misc.IdentifierNode.Construct(node, 'PCI_TIP_OPTIONS_DISABLED', '8', ''))
    node.AddChild(misc.IdentifierNode.Construct(node,
                                                'PCI_TIP_DISABLED_BY_POLICY', '9', ''))

