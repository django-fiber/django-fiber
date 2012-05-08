
/*
Copyright 2012 Marco Braak

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

(function() {
  var $, BorderDropHint, DragElement, FolderElement, GhostDropHint, Json, Node, NodeElement, Position, indexOf, toJson,
    __hasProp = Object.prototype.hasOwnProperty,
    __extends = function(child, parent) { for (var key in parent) { if (__hasProp.call(parent, key)) child[key] = parent[key]; } function ctor() { this.constructor = child; } ctor.prototype = parent.prototype; child.prototype = new ctor; child.__super__ = parent.prototype; return child; };

  this.Tree = {};

  $ = this.jQuery;

  indexOf = function(array, item) {
    var i, value, _len;
    if (array.indexOf) {
      return array.indexOf(item);
    } else {
      for (i = 0, _len = array.length; i < _len; i++) {
        value = array[i];
        if (value === item) return i;
      }
      return -1;
    }
  };

  this.Tree.indexOf = indexOf;

  Json = {};

  Json.escapable = /[\\\"\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]/g;

  Json.meta = {
    '\b': '\\b',
    '\t': '\\t',
    '\n': '\\n',
    '\f': '\\f',
    '\r': '\\r',
    '"': '\\"',
    '\\': '\\\\'
  };

  Json.quote = function(string) {
    Json.escapable.lastIndex = 0;
    if (Json.escapable.test(string)) {
      return '"' + string.replace(Json.escapable, function(a) {
        var c;
        c = Json.meta[a];
        return (type(c === 'string') ? c : '\\u' + ('0000' + a.charCodeAt(0).toString(16)).slice(-4));
      }) + '"';
    } else {
      return '"' + string + '"';
    }
  };

  Json.str = function(key, holder) {
    var i, k, partial, v, value, _len;
    value = holder[key];
    if (value && typeof value === 'object' && value.toJSON === 'function') {
      value = value.toJSON(key);
    }
    switch (typeof value) {
      case 'string':
        return Json.quote(value);
      case 'number':
        if (isFinite(value)) {
          return String(value);
        } else {
          return 'null';
        }
      case 'boolean':
      case 'null':
        return String(value);
      case 'object':
        if (!value) return 'null';
        partial = [];
        if (Object.prototype.toString.apply(value) === '[object Array]') {
          for (i = 0, _len = value.length; i < _len; i++) {
            v = value[i];
            partial[i] = Json.str(i, value) || 'null';
          }
          return (partial.length === 0 ? '[]' : '[' + partial.join(',') + ']');
        }
        for (k in value) {
          if (Object.prototype.hasOwnProperty.call(value, k)) {
            v = Json.str(k, value);
            if (v) partial.push(Json.quote(k) + ':' + v);
          }
        }
        return (partial.length === 0 ? '{}' : '{' + partial.join(',') + '}');
    }
  };

  toJson = function(value) {
    return Json.str('', {
      '': value
    });
  };

  this.Tree.toJson = toJson;

  Position = {
    getName: function(position) {
      if (position === Position.BEFORE) {
        return 'before';
      } else if (position === Position.AFTER) {
        return 'after';
      } else if (position === Position.INSIDE) {
        return 'inside';
      } else {
        return 'none';
      }
    }
  };

  Position.BEFORE = 1;

  Position.AFTER = 2;

  Position.INSIDE = 3;

  Position.NONE = 4;

  this.Tree.Position = Position;

  Node = (function() {

    function Node(name) {
      this.init(name);
    }

    Node.prototype.init = function(name) {
      this.name = name;
      this.children = [];
      return this.parent = null;
    };

    Node.prototype.initFromData = function(data) {
      var addChildren, addNode,
        _this = this;
      addNode = function(node_data) {
        return $.each(node_data, function(key, value) {
          if (key === 'children') {
            addChildren(value);
          } else if (key === 'label') {
            _this['name'] = value;
          } else {
            _this[key] = value;
          }
          return true;
        });
      };
      addChildren = function(children_data) {
        var child, node, _i, _len, _results;
        _results = [];
        for (_i = 0, _len = children_data.length; _i < _len; _i++) {
          child = children_data[_i];
          node = new Node();
          node.initFromData(child);
          _results.push(_this.addChild(node));
        }
        return _results;
      };
      return addNode(data);
    };

    /*
        Create tree from data.
    
        Structure of data is:
        [
            {
                label: 'node1',
                children: [
                    { label: 'child1' },
                    { label: 'child2' }
                ]
            },
            {
                label: 'node2'
            }
        ]
    */

    Node.prototype.loadFromData = function(data) {
      var node, o, _i, _len, _results,
        _this = this;
      this.children = [];
      _results = [];
      for (_i = 0, _len = data.length; _i < _len; _i++) {
        o = data[_i];
        node = new Node(o.label);
        $.each(o, function(key, value) {
          if (key !== 'label') node[key] = value;
          return true;
        });
        this.addChild(node);
        if (o.children) {
          _results.push(node.loadFromData(o.children));
        } else {
          _results.push(void 0);
        }
      }
      return _results;
    };

    /*
        Add child.
    
        tree.addChild(
            new Node('child1')
        );
    */

    Node.prototype.addChild = function(node) {
      this.children.push(node);
      return node.parent = this;
    };

    /*
        Add child at position. Index starts at 0.
    
        tree.addChildAtPosition(
            new Node('abc'),
            1
        );
    */

    Node.prototype.addChildAtPosition = function(node, index) {
      this.children.splice(index, 0, node);
      return node.parent = this;
    };

    /*
        Remove child.
    
        tree.removeChile(tree.children[0]);
    */

    Node.prototype.removeChild = function(node) {
      return this.children.splice(this.getChildIndex(node), 1);
    };

    /*
        Get child index.
    
        var index = getChildIndex(node);
    */

    Node.prototype.getChildIndex = function(node) {
      return $.inArray(node, this.children);
    };

    /*
        Does the tree have children?
    
        if (tree.hasChildren()) {
            //
        }
    */

    Node.prototype.hasChildren = function() {
      return this.children.length !== 0;
    };

    /*
        Iterate over all the nodes in the tree.
    
        Calls callback with (node, level).
    
        The callback must return true to continue the iteration on current node.
    
        tree.iterate(
            function(node, level) {
               console.log(node.name);
    
               // stop iteration after level 2
               return (level <= 2);
            }
        );
    */

    Node.prototype.iterate = function(callback, level) {
      var _iterate,
        _this = this;
      _iterate = function(level) {
        var child, result, _i, _len, _ref, _results;
        _ref = _this.children;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          child = _ref[_i];
          result = callback(child, level);
          if (_this.hasChildren() && result) {
            _results.push(child.iterate(callback, level + 1));
          } else {
            _results.push(void 0);
          }
        }
        return _results;
      };
      return _iterate(0);
    };

    /*
        Move node relative to another node.
    
        Argument position: Position.BEFORE, Position.AFTER or Position.Inside
    
        // move node1 after node2
        tree.moveNode(node1, node2, Position.AFTER);
    */

    Node.prototype.moveNode = function(moved_node, target_node, position) {
      moved_node.parent.removeChild(moved_node);
      if (position === Position.AFTER) {
        return target_node.parent.addChildAtPosition(moved_node, target_node.parent.getChildIndex(target_node) + 1);
      } else if (position === Position.BEFORE) {
        return target_node.parent.addChildAtPosition(moved_node, target_node.parent.getChildIndex(target_node));
      } else if (position === Position.INSIDE) {
        return target_node.addChildAtPosition(moved_node, 0);
      }
    };

    /*
        Get the tree as data.
    */

    Node.prototype.getData = function() {
      var getDataFromNodes,
        _this = this;
      getDataFromNodes = function(nodes) {
        var data, k, node, tmp_node, v, _i, _len;
        data = [];
        for (_i = 0, _len = nodes.length; _i < _len; _i++) {
          node = nodes[_i];
          tmp_node = {};
          for (k in node) {
            v = node[k];
            if ((k !== 'parent' && k !== 'children' && k !== 'element') && Object.prototype.hasOwnProperty.call(node, k)) {
              tmp_node[k] = v;
            }
          }
          if (node.hasChildren()) {
            tmp_node.children = getDataFromNodes(node.children);
          }
          data.push(tmp_node);
        }
        return data;
      };
      return getDataFromNodes(this.children);
    };

    return Node;

  })();

  this.Tree.Tree = Node;

  $.widget("ui.tree", $.ui.mouse, {
    widgetEventPrefix: "tree",
    options: {
      autoOpen: false,
      saveState: false,
      dragAndDrop: false,
      selectable: false,
      onCanSelectNode: null,
      onSetStateFromStorage: null,
      onGetStateFromStorage: null,
      onCreateLi: null,
      onIsMoveHandle: null,
      onCanMove: null,
      onCanMoveTo: null
    },
    _create: function() {
      var node_element;
      this.tree = new Node();
      this.tree.loadFromData(this.options.data);
      this.selected_node = null;
      this._openNodes();
      this._createDomElements(this.tree);
      if (this.selected_node) {
        node_element = this._getNodeElementForNode(this.selected_node);
        if (node_element) node_element.select();
      }
      this.element.click($.proxy(this._click, this));
      this.element.bind('contextmenu', $.proxy(this._contextmenu, this));
      this._mouseInit();
      this.hovered_area = null;
      this.$ghost = null;
      return this.hit_areas = [];
    },
    destroy: function() {
      this.element.empty();
      this.element.unbind();
      this.tree = null;
      this._mouseDestroy();
      return $.Widget.prototype.destroy.call(this);
    },
    getTree: function() {
      return this.tree;
    },
    toJson: function() {
      return toJson(this.tree.getData());
    },
    addNode: function(data) {
      var n;
      n = new Node();
      n.initFromData(data);
      this.getTree().addChild(n);
      this.element.empty();
      return this._createDomElements(this.getTree());
    },
    toggle: function(node, on_finished) {
      if (node.hasChildren()) new FolderElement(node).toggle(on_finished);
      if (this.options.saveState) return this._saveState();
    },
    selectNode: function(node) {
      if (this.options.selectable) {
        if (this.selected_node) {
          this._getNodeElementForNode(this.selected_node).deselect();
        }
        this._getNodeElementForNode(node).select();
        this.selected_node = node;
        if (this.options.saveState) return this._saveState();
      }
    },
    getSelectedNode: function() {
      return this.selected_node || false;
    },
    _getState: function() {
      var open_nodes, selected_node,
        _this = this;
      open_nodes = [];
      this.tree.iterate(function(node) {
        if (node.is_open && node.id && node.hasChildren()) {
          open_nodes.push(node.id);
        }
        return true;
      });
      selected_node = '';
      if (this.selected_node) selected_node = this.selected_node.id;
      return toJson({
        open_nodes: open_nodes,
        selected_node: selected_node
      });
    },
    _setState: function(state) {
      var data, open_nodes, selected_node_id,
        _this = this;
      data = $.parseJSON(state);
      open_nodes = data.open_nodes;
      selected_node_id = data.selected_node;
      return this.tree.iterate(function(node) {
        if (node.id && node.hasChildren() && (indexOf(open_nodes, node.id) >= 0)) {
          node.is_open = true;
        }
        if (selected_node_id && (node.id === selected_node_id)) {
          _this.selected_node = node;
        }
        return true;
      });
    },
    _saveState: function() {
      if (this.options.onSetStateFromStorage) {
        return this.options.onSetStateFromStorage(this._getState());
      } else {
        if ($.cookie) {
          return $.cookie(this._getCookieName(), this._getState(), {
            path: '/'
          });
        }
      }
    },
    _restoreState: function() {
      var state;
      if (this.options.onGetStateFromStorage) {
        state = this.options.onGetStateFromStorage();
      } else {
        if ($.cookie) {
          state = $.cookie(this._getCookieName(), {
            path: '/'
          });
        } else {
          state = null;
        }
      }
      if (!state) {
        return false;
      } else {
        this._setState(state);
        return true;
      }
    },
    _getCookieName: function() {
      if (typeof this.options.saveState === 'string') {
        return this.options.saveState;
      } else {
        return 'tree';
      }
    },
    _createDomElements: function(tree) {
      var createFolderLi, createLi, createNodeLi, createUl, doCreateDomElements,
        _this = this;
      createUl = function(depth, is_open) {
        var class_string;
        if (depth) {
          class_string = '';
        } else {
          class_string = ' class="tree"';
        }
        return $("<ul" + class_string + "></ul>");
      };
      createLi = function(node) {
        var $li;
        if (node.hasChildren()) {
          $li = createFolderLi(node);
        } else {
          $li = createNodeLi(node);
        }
        if (_this.options.onCreateLi) _this.options.onCreateLi(node, $li);
        return $li;
      };
      createNodeLi = function(node) {
        return $("<li><div><span class=\"title\">" + node.name + "</span></div></li>");
      };
      createFolderLi = function(node) {
        var button_class, folder_class, getButtonClass, getFolderClass;
        getButtonClass = function() {
          var classes;
          classes = ['toggler'];
          if (!node.is_open) classes.push('closed');
          return classes.join(' ');
        };
        getFolderClass = function() {
          var classes;
          classes = ['folder'];
          if (!node.is_open) classes.push('closed');
          return classes.join(' ');
        };
        button_class = getButtonClass();
        folder_class = getFolderClass();
        return $("<li class=\"" + folder_class + "\"><div><a class=\"" + button_class + "\">&raquo;</a><span class=\"title\">" + node.name + "</span></div></li>");
      };
      doCreateDomElements = function($element, children, depth, is_open) {
        var $li, $ul, child, _i, _len, _results;
        $ul = createUl(depth, is_open);
        $element.append($ul);
        _results = [];
        for (_i = 0, _len = children.length; _i < _len; _i++) {
          child = children[_i];
          $li = createLi(child);
          $ul.append($li);
          child.element = $li[0];
          $li.data('node', child);
          if (child.hasChildren()) {
            _results.push(doCreateDomElements($li, child.children, depth + 1, child.is_open));
          } else {
            _results.push(void 0);
          }
        }
        return _results;
      };
      return doCreateDomElements(this.element, tree.children, 0, true);
    },
    _click: function(e) {
      var $target, event, node, node_element;
      if (e.ctrlKey) return;
      $target = $(e.target);
      if ($target.is('.toggler')) {
        node_element = this._getNodeElement($target);
        if (node_element && node_element.node.hasChildren()) {
          node_element.toggle();
          if (this.options.saveState) this._saveState();
          e.preventDefault();
          return e.stopPropagation();
        }
      } else if ($target.is('div') || $target.is('span')) {
        node = this._getNode($target);
        if (node) {
          if ((!this.options.onCanSelectNode) || this.options.onCanSelectNode(node)) {
            this.selectNode(node);
            event = jQuery.Event('tree.click');
            event.node = node;
            return this.element.trigger(event);
          }
        }
      }
    },
    _contextmenu: function(e) {
      var $div, event, node;
      $div = $(e.target).closest('ul.tree div');
      if ($div.length) {
        node = this._getNode($div);
        if (node) {
          e.preventDefault();
          e.stopPropagation();
          event = jQuery.Event('tree.contextmenu');
          event.node = node;
          event.click_event = e;
          this.element.trigger(event);
          return false;
        }
      }
    },
    _getNode: function($element) {
      var $li;
      $li = $element.closest('li');
      if ($li.length === 0) {
        return null;
      } else {
        return $li.data('node');
      }
    },
    _getNodeElement: function($element) {
      var node;
      node = this._getNode($element);
      if (node) {
        return this._getNodeElementForNode(node);
      } else {
        return null;
      }
    },
    _getNodeElementForNode: function(node) {
      if (node.hasChildren()) {
        return new FolderElement(node);
      } else {
        return new NodeElement(node);
      }
    },
    _mouseCapture: function(event) {
      var $element, node_element;
      if (!this.options.dragAndDrop) return;
      $element = $(event.target);
      if (this.options.onIsMoveHandle && !this.options.onIsMoveHandle($element)) {
        return null;
      }
      node_element = this._getNodeElement($(event.target));
      if (node_element && this.options.onCanMove) {
        if (!this.options.onCanMove(node_element.node)) node_element = null;
      }
      this.current_item = node_element;
      return this.current_item !== null;
    },
    _mouseStart: function(event) {
      var offsetX, offsetY, _ref;
      if (!this.options.dragAndDrop) return;
      this._refreshHitAreas();
      _ref = this._getOffsetFromEvent(event), offsetX = _ref[0], offsetY = _ref[1];
      this.drag_element = new DragElement(this.current_item.node, offsetX, offsetY, this.element);
      this.current_item.$element.addClass('moving');
      return true;
    },
    _getOffsetFromEvent: function(event) {
      var element_offset;
      element_offset = $(event.target).offset();
      return [event.pageX - element_offset.left, event.pageY - element_offset.top];
    },
    _mouseDrag: function(event) {
      var area, position_name;
      if (!this.options.dragAndDrop) return;
      this.drag_element.move(event.pageX, event.pageY);
      area = this.findHoveredArea(event.pageX, event.pageY);
      if (area && this.options.onCanMoveTo) {
        position_name = Position.getName(area.position);
        if (!this.options.onCanMoveTo(this.current_item.node, area.node, position_name)) {
          area = null;
        }
      }
      if (!area) {
        this._removeDropHint();
        this._removeHover();
        this._stopOpenFolderTimer();
      } else {
        if (this.hovered_area !== area) {
          this.hovered_area = area;
          this._updateDropHint();
        }
      }
      return true;
    },
    _updateDropHint: function() {
      var node, node_element;
      this._stopOpenFolderTimer();
      if (!this.hovered_area) return;
      node = this.hovered_area.node;
      if (node.hasChildren() && !node.is_open && this.hovered_area.position === Position.INSIDE) {
        this._startOpenFolderTimer(node);
      }
      this._removeDropHint();
      node_element = this._getNodeElementForNode(this.hovered_area.node);
      return this.previous_ghost = node_element.addDropHint(this.hovered_area.position);
    },
    _mouseStop: function() {
      if (!this.options.dragAndDrop) return;
      this._moveItem();
      this._clear();
      this._removeHover();
      this._removeDropHint();
      this._removeHitAreas();
      this.current_item.$element.removeClass('moving');
      return false;
    },
    _mouseMove: function(event) {
      if ($.browser.msie && document.documentMode === 8 && !event.button) {
        event.button = 1;
      }
      return $.ui.mouse.prototype._mouseMove.call(this, event);
    },
    _moveItem: function() {
      var event;
      if (this.hovered_area && this.hovered_area.position !== Position.NONE) {
        this.tree.moveNode(this.current_item.node, this.hovered_area.node, this.hovered_area.position);
        if (this.hovered_area.position === Position.INSIDE) {
          this.hovered_area.node.is_open = true;
        }
        event = jQuery.Event('tree.move');
        event.move_info = {
          moved_node: this.current_item.node,
          target_node: this.hovered_area.node,
          position: Position.getName(this.hovered_area.position)
        };
        this.element.trigger(event);
        this.element.empty();
        return this._createDomElements(this.tree);
      }
    },
    _clear: function() {
      this.drag_element.remove();
      return this.drag_element = null;
    },
    _refreshHitAreas: function() {
      this._removeHitAreas();
      return this._generateHitAreas();
    },
    _generateHitAreas: function() {
      var addPosition, getTop, groupPositions, handleAfterOpenFolder, handleClosedFolder, handleFirstNode, handleNode, handleOpenFolder, hit_areas, last_top, positions,
        _this = this;
      positions = [];
      last_top = 0;
      getTop = function($element) {
        return $element.offset().top;
      };
      addPosition = function(node, position, top) {
        positions.push({
          top: top,
          node: node,
          position: position
        });
        return last_top = top;
      };
      groupPositions = function(handle_group) {
        var group, position, previous_top, _i, _len;
        previous_top = -1;
        group = [];
        for (_i = 0, _len = positions.length; _i < _len; _i++) {
          position = positions[_i];
          if (position.top !== previous_top) {
            if (group.length) handle_group(group, previous_top, position.top);
            previous_top = position.top;
            group = [];
          }
          group.push(position);
        }
        return handle_group(group, previous_top, _this.element.offset().top + _this.element.height());
      };
      handleNode = function(node, next_node, $element) {
        var top;
        top = getTop($element);
        if (node === _this.current_item.node) {
          addPosition(node, Position.NONE, top);
        } else {
          addPosition(node, Position.INSIDE, top);
        }
        if (next_node === _this.current_item.node || node === _this.current_item.node) {
          return addPosition(node, Position.NONE, top);
        } else {
          return addPosition(node, Position.AFTER, top);
        }
      };
      handleOpenFolder = function(node, $element) {
        if (node === _this.current_item.node) return false;
        if (node.children[0] !== _this.current_item.node) {
          addPosition(node, Position.INSIDE, getTop($element));
        }
        return true;
      };
      handleAfterOpenFolder = function(node, next_node, $element) {
        if (node === _this.current_item.node || next_node === _this.current_item.node) {
          return addPosition(node, Position.NONE, last_top);
        } else {
          return addPosition(node, Position.AFTER, last_top);
        }
      };
      handleClosedFolder = function(node, next_node, $element) {
        var top;
        top = getTop($element);
        if (node === _this.current_item.node) {
          return addPosition(node, Position.NONE, top);
        } else {
          addPosition(node, Position.INSIDE, top);
          if (next_node !== _this.current_item.node) {
            return addPosition(node, Position.AFTER, top);
          }
        }
      };
      handleFirstNode = function(node, $element) {
        if (node !== _this.current_item.node) {
          return addPosition(node, Position.BEFORE, getTop($(node.element)));
        }
      };
      this._iterateVisibleNodes(handleNode, handleOpenFolder, handleClosedFolder, handleAfterOpenFolder, handleFirstNode);
      hit_areas = [];
      groupPositions(function(positions_in_group, top, bottom) {
        var area_height, area_top, position, _i, _len, _results;
        area_height = (bottom - top) / positions_in_group.length;
        area_top = top;
        _results = [];
        for (_i = 0, _len = positions_in_group.length; _i < _len; _i++) {
          position = positions_in_group[_i];
          hit_areas.push({
            top: area_top,
            bottom: area_top + area_height,
            node: position.node,
            position: position.position
          });
          _results.push(area_top += area_height);
        }
        return _results;
      });
      return this.hit_areas = hit_areas;
    },
    findHoveredArea: function(x, y) {
      var area, high, low, mid, tree_offset;
      tree_offset = this.element.offset();
      if (x < tree_offset.left || y < tree_offset.top || x > (tree_offset.left + this.element.width()) || y > (tree_offset.top + this.element.height())) {
        return null;
      }
      low = 0;
      high = this.hit_areas.length;
      while (low < high) {
        mid = (low + high) >> 1;
        area = this.hit_areas[mid];
        if (y < area.top) {
          high = mid;
        } else if (y > area.bottom) {
          low = mid + 1;
        } else {
          return area;
        }
      }
      return null;
    },
    _iterateVisibleNodes: function(handle_node, handle_open_folder, handle_closed_folder, handle_after_open_folder, handle_first_node) {
      var is_first_node, iterate,
        _this = this;
      is_first_node = true;
      iterate = function(node, next_node) {
        var $element, child, children_length, i, must_iterate_inside, _len, _ref;
        must_iterate_inside = (node.is_open || !node.element) && node.hasChildren();
        if (node.element) {
          $element = $(node.element);
          if (!$element.is(':visible')) return;
          if (is_first_node) {
            handle_first_node(node, $element);
            is_first_node = false;
          }
          if (!node.hasChildren()) {
            handle_node(node, next_node, $element);
          } else if (node.is_open) {
            if (!handle_open_folder(node, $element)) must_iterate_inside = false;
          } else {
            handle_closed_folder(node, next_node, $element);
          }
        }
        if (must_iterate_inside) {
          children_length = node.children.length;
          _ref = node.children;
          for (i = 0, _len = _ref.length; i < _len; i++) {
            child = _ref[i];
            if (i === (children_length - 1)) {
              iterate(node.children[i], null);
            } else {
              iterate(node.children[i], node.children[i + 1]);
            }
          }
          if (node.is_open) {
            return handle_after_open_folder(node, next_node, $element);
          }
        }
      };
      return iterate(this.tree);
    },
    _removeHover: function() {
      return this.hovered_area = null;
    },
    _removeDropHint: function() {
      if (this.previous_ghost) return this.previous_ghost.remove();
    },
    _removeHitAreas: function() {
      return this.hit_areas = [];
    },
    _openNodes: function() {
      var max_level;
      if (this.options.saveState) if (this._restoreState()) return;
      if (this.options.autoOpen === false) {
        return;
      } else if (this.options.autoOpen === true) {
        max_level = -1;
      } else {
        max_level = parseInt(this.options.autoOpen);
      }
      return this.tree.iterate(function(node, level) {
        node.is_open = true;
        return level !== max_level;
      });
    },
    _startOpenFolderTimer: function(folder) {
      var openFolder,
        _this = this;
      openFolder = function() {
        return _this._getNodeElementForNode(folder).open(function() {
          _this._refreshHitAreas();
          return _this._updateDropHint();
        });
      };
      return this.open_folder_timer = setTimeout(openFolder, 500);
    },
    _stopOpenFolderTimer: function() {
      if (this.open_folder_timer) {
        clearTimeout(this.open_folder_timer);
        return this.open_folder_timer = null;
      }
    }
  });

  GhostDropHint = (function() {

    function GhostDropHint(node, $element, position) {
      this.$element = $element;
      this.node = node;
      this.$ghost = $('<li class="ghost"><span class="circle"></span><span class="line"></span></li>');
      if (position === Position.AFTER) {
        this.moveAfter();
      } else if (position === Position.BEFORE) {
        this.moveBefore();
      } else if (position === Position.INSIDE) {
        if (node.hasChildren() && node.is_open) {
          this.moveInsideOpenFolder();
        } else {
          this.moveInside();
        }
      }
    }

    GhostDropHint.prototype.remove = function() {
      return this.$ghost.remove();
    };

    GhostDropHint.prototype.moveAfter = function() {
      return this.$element.after(this.$ghost);
    };

    GhostDropHint.prototype.moveBefore = function() {
      return this.$element.before(this.$ghost);
    };

    GhostDropHint.prototype.moveInsideOpenFolder = function() {
      return $(this.node.children[0].element).before(this.$ghost);
    };

    GhostDropHint.prototype.moveInside = function() {
      this.$element.after(this.$ghost);
      return this.$ghost.addClass('inside');
    };

    return GhostDropHint;

  })();

  BorderDropHint = (function() {

    function BorderDropHint($element) {
      var $div, width;
      $div = $element.children('div');
      width = $element.width() - 4;
      this.$hint = $('<span class="border"></span>');
      $div.append(this.$hint);
      this.$hint.css({
        width: width,
        height: $div.height() - 4
      });
    }

    BorderDropHint.prototype.remove = function() {
      return this.$hint.remove();
    };

    return BorderDropHint;

  })();

  NodeElement = (function() {

    function NodeElement(node) {
      this.init(node);
    }

    NodeElement.prototype.init = function(node) {
      this.node = node;
      return this.$element = $(node.element);
    };

    NodeElement.prototype.getUl = function() {
      return this.$element.children('ul:first');
    };

    NodeElement.prototype.getSpan = function() {
      return this.$element.children('div').find('span.title');
    };

    NodeElement.prototype.getLi = function() {
      return this.$element;
    };

    NodeElement.prototype.addDropHint = function(position) {
      if (position === Position.INSIDE) {
        return new BorderDropHint(this.$element);
      } else {
        return new GhostDropHint(this.node, this.$element, position);
      }
    };

    NodeElement.prototype.select = function() {
      return this.getLi().addClass('selected');
    };

    NodeElement.prototype.deselect = function() {
      return this.getLi().removeClass('selected');
    };

    return NodeElement;

  })();

  FolderElement = (function(_super) {

    __extends(FolderElement, _super);

    function FolderElement() {
      FolderElement.__super__.constructor.apply(this, arguments);
    }

    FolderElement.prototype.toggle = function(on_finished) {
      if (this.node.is_open) {
        return this.close(on_finished);
      } else {
        return this.open(on_finished);
      }
    };

    FolderElement.prototype.open = function(on_finished) {
      this.node.is_open = true;
      this.getButton().removeClass('closed');
      return this.getUl().slideDown('fast', $.proxy(function() {
        this.getLi().removeClass('closed');
        if (on_finished) return on_finished();
      }, this));
    };

    FolderElement.prototype.close = function(on_finished) {
      this.node.is_open = false;
      this.getButton().addClass('closed');
      return this.getUl().slideUp('fast', $.proxy(function() {
        this.getLi().addClass('closed');
        if (on_finished) return on_finished();
      }, this));
    };

    FolderElement.prototype.getButton = function() {
      return this.$element.children('div').find('a.toggler');
    };

    FolderElement.prototype.addDropHint = function(position) {
      if (!this.node.is_open && position === Position.INSIDE) {
        return new BorderDropHint(this.$element);
      } else {
        return new GhostDropHint(this.node, this.$element, position);
      }
    };

    return FolderElement;

  })(NodeElement);

  DragElement = (function() {

    function DragElement(node, offset_x, offset_y, $tree) {
      this.offset_x = offset_x;
      this.offset_y = offset_y;
      this.$element = $("<span class=\"title tree-dragging\">" + node.name + "</span>");
      this.$element.css("position", "absolute");
      $tree.append(this.$element);
    }

    DragElement.prototype.move = function(page_x, page_y) {
      return this.$element.offset({
        left: page_x - this.offset_x,
        top: page_y - this.offset_y
      });
    };

    DragElement.prototype.remove = function() {
      return this.$element.remove();
    };

    return DragElement;

  })();

  this.Tree.Node = Node;

}).call(this);
