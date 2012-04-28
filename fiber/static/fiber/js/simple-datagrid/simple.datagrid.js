
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
  var $, SortOrder, buildUrl, slugify;

  $ = this.jQuery;

  slugify = function(string) {
    return string.replace(/\s+/g, '-').replace(/[^a-zA-Z0-9\-]/g, '').toLowerCase();
  };

  buildUrl = function(url, query_parameters) {
    if (query_parameters) {
      return url + '?' + $.param(query_parameters);
    } else {
      return url;
    }
  };

  this.SimpleDataGrid = {
    slugify: slugify,
    buildUrl: buildUrl
  };

  SortOrder = {
    ASCENDING: 1,
    DESCENDING: 2
  };

  $.widget("ui.simple_datagrid", {
    options: {
      onGetData: null,
      order_by: null,
      url: null,
      data: null
    },
    _create: function() {
      this.url = this._getBaseUrl();
      this.$selected_row = null;
      this.current_page = 1;
      this.parameters = {};
      this.order_by = this.options.order_by;
      this.sort_order = SortOrder.ASCENDING;
      this._generateColumnData();
      this._createDomElements();
      this._bindEvents();
      return this._loadData();
    },
    destroy: function() {
      this._removeDomElements();
      this._removeEvents();
      return $.Widget.prototype.destroy.call(this);
    },
    getSelectedRow: function() {
      if (this.$selected_row) {
        return this.$selected_row.data('row');
      } else {
        return null;
      }
    },
    reload: function() {
      return this._loadData();
    },
    loadData: function(data) {
      return this._fillGrid(data);
    },
    setParameter: function(key, value) {
      return this.parameters[key] = value;
    },
    getColumns: function() {
      return this.columns;
    },
    setCurrentPage: function(page) {
      return this.current_page = page;
    },
    _generateColumnData: function() {
      var generateFromOptions, generateFromThElements,
        _this = this;
      generateFromThElements = function() {
        var $th_elements;
        $th_elements = _this.element.find('th');
        _this.columns = [];
        return $th_elements.each(function(i, th) {
          var $th, key, title;
          $th = $(th);
          title = $th.text();
          key = $th.data('key') || slugify(title);
          return _this.columns.push({
            title: title,
            key: key
          });
        });
      };
      generateFromOptions = function() {
        var column, column_info, _i, _len, _ref, _results;
        _this.columns = [];
        _ref = _this.options.columns;
        _results = [];
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          column = _ref[_i];
          if (typeof column === 'object') {
            column_info = {
              title: column.title,
              key: column.key,
              on_generate: column.on_generate
            };
          } else {
            column_info = {
              title: column,
              key: slugify(column)
            };
          }
          _results.push(_this.columns.push(column_info));
        }
        return _results;
      };
      if (this.options.columns) {
        return generateFromOptions();
      } else {
        return generateFromThElements();
      }
    },
    _createDomElements: function() {
      var initBody, initFoot, initHead, initTable,
        _this = this;
      initTable = function() {
        return _this.element.addClass('simple-data-grid');
      };
      initBody = function() {
        _this.$tbody = _this.element.find('tbody');
        if (_this.$tbody.length) {
          return _this.$tbody.empty();
        } else {
          _this.$tbody = $('<tbody></tbody>');
          return _this.element.append(_this.$tbody);
        }
      };
      initFoot = function() {
        _this.$tfoot = _this.element.find('tfoot');
        if (_this.$tfoot.length) {
          return _this.$tfoot.empty();
        } else {
          _this.$tfoot = $('<tfoot></tfoot>');
          return _this.element.append(_this.$tfoot);
        }
      };
      initHead = function() {
        _this.$thead = _this.element.find('thead');
        if (_this.$thead.length) {
          return _this.$thead.empty();
        } else {
          _this.$thead = $('<thead></thead>');
          return _this.element.append(_this.$thead);
        }
      };
      initTable();
      initHead();
      initBody();
      return initFoot();
    },
    _removeDomElements: function() {
      this.element.removeClass('simple-data-grid');
      this.$tbody.remove();
      return this.$tbody = null;
    },
    _bindEvents: function() {
      this.element.delegate('tbody tr', 'click', $.proxy(this._clickRow, this));
      this.element.delegate('thead th a', 'click', $.proxy(this._clickHeader, this));
      this.element.delegate('.paginator .first', 'click', $.proxy(this._handleClickFirstPage, this));
      this.element.delegate('.paginator .previous', 'click', $.proxy(this._handleClickPreviousPage, this));
      this.element.delegate('.paginator .next', 'click', $.proxy(this._handleClickNextPage, this));
      return this.element.delegate('.paginator .last', 'click', $.proxy(this._handleClickLastPage, this));
    },
    _removeEvents: function() {
      this.element.undelegate('tbody tr', 'click');
      this.element.undelegate('tbody thead th a', 'click');
      this.element.undelegate('.paginator .first', 'click');
      this.element.undelegate('.paginator .previous', 'click');
      this.element.undelegate('.paginator .next', 'click');
      return this.element.undelegate('.paginator .last', 'click');
    },
    _getBaseUrl: function() {
      var url;
      url = this.options.url;
      if (url) {
        return url;
      } else {
        return this.element.data('url');
      }
    },
    _clickRow: function(e) {
      var $tr, event;
      if (this.$selected_row) this.$selected_row.removeClass('selected');
      $tr = $(e.target).closest('tr');
      $tr.addClass('selected');
      this.$selected_row = $tr;
      event = $.Event('datagrid.select');
      return this.element.trigger(event);
    },
    _loadData: function() {
      var getDataFromArray, getDataFromCallback, getDataFromUrl, query_parameters,
        _this = this;
      query_parameters = $.extend({}, this.parameters, {
        page: this.current_page
      });
      if (this.order_by) {
        query_parameters.order_by = this.order_by;
        if (this.sort_order === SortOrder.DESCENDING) {
          query_parameters.sortorder = 'desc';
        } else {
          query_parameters.sortorder = 'asc';
        }
      }
      getDataFromCallback = function() {
        return _this.options.onGetData(query_parameters, $.proxy(_this._fillGrid, _this));
      };
      getDataFromUrl = function() {
        var url;
        url = buildUrl(_this.url, query_parameters);
        return $.ajax({
          url: url,
          success: function(result) {
            return _this._fillGrid(result);
          },
          datatType: 'json',
          cache: false
        });
      };
      getDataFromArray = function() {
        return _this._fillGrid(_this.options.data);
      };
      if (this.options.onGetData) {
        return getDataFromCallback();
      } else if (this.url) {
        return getDataFromUrl();
      } else if (this.options.data) {
        return getDataFromArray();
      } else {
        return this._fillGrid([]);
      }
    },
    _fillGrid: function(data) {
      var addRowFromArray, addRowFromObject, fillFooter, fillHeader, fillRows, generateTr, rows, total_pages,
        _this = this;
      addRowFromObject = function(row) {
        var column, html, value, _i, _len, _ref;
        html = '';
        _ref = _this.columns;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          column = _ref[_i];
          if (column.key in row) {
            value = row[column.key];
            if (column.on_generate) value = column.on_generate(value, row);
          } else {
            value = '';
          }
          html += "<td>" + value + "</td>";
        }
        return html;
      };
      addRowFromArray = function(row) {
        var column, html, i, value, _len;
        html = '';
        for (i = 0, _len = row.length; i < _len; i++) {
          value = row[i];
          column = _this.columns[i];
          if (column.on_generate) value = column.on_generate(value, row);
          html += "<td>" + value + "</td>";
        }
        return html;
      };
      generateTr = function(row) {
        var data_string;
        if (row.id) {
          data_string = " data-id=\"" + row.id + "\"";
        } else {
          data_string = "";
        }
        return "<tr" + data_string + ">";
      };
      fillRows = function(rows) {
        var $tr, html, row, _i, _len, _results;
        _this.$tbody.empty();
        _results = [];
        for (_i = 0, _len = rows.length; _i < _len; _i++) {
          row = rows[_i];
          html = generateTr(row);
          if ($.isArray(row)) {
            html += addRowFromArray(row);
          } else {
            html += addRowFromObject(row);
          }
          html += '</tr>';
          $tr = $(html);
          $tr.data('row', row);
          _results.push(_this.$tbody.append($tr));
        }
        return _results;
      };
      fillFooter = function(total_pages, row_count) {
        var html;
        if (!total_pages || total_pages === 1) {
          if (row_count === 0) {
            html = "<tr><td colspan=\"" + _this.columns.length + "\">No rows</td></tr>";
          } else {
            html = '';
          }
        } else {
          html = "<tr><td class=\"paginator\" colspan=\"" + _this.columns.length + "\">";
          if (!_this.current_page || _this.current_page === 1) {
            html += '<span class="sprite-icons-first-disabled">first</span>';
            html += '<span class="sprite-icons-previous-disabled">previous</span>';
          } else {
            html += "<a href=\"#\" class=\"sprite-icons-first first\">first</a>";
            html += "<a href=\"#\" class=\"sprite-icons-previous previous\">previous</a>";
          }
          html += "<span>page " + _this.current_page + " of " + total_pages + "</span>";
          if (!_this.current_page || _this.current_page === total_pages) {
            html += '<span class="sprite-icons-next-disabled">next</span>';
            html += '<span class="sprite-icons-last-disabled">last</span>';
          } else {
            html += "<a href=\"#\" class=\"sprite-icons-next next\">next</a>";
            html += "<a href=\"#\" class=\"sprite-icons-last last\">last</a>";
          }
          html += "</td></tr>";
        }
        return _this.$tfoot.html(html);
      };
      fillHeader = function() {
        var class_html, column, html, _i, _len, _ref;
        html = '<tr>';
        _ref = _this.columns;
        for (_i = 0, _len = _ref.length; _i < _len; _i++) {
          column = _ref[_i];
          html += "<th data-key=\"" + column.key + "\">";
          if (!_this.order_by) {
            html += column.title;
          } else {
            html += "<a href=\"#\">" + column.title;
            if (column.key === _this.order_by) {
              class_html = "sort ";
              if (_this.sort_order === SortOrder.DESCENDING) {
                class_html += "asc sprite-icons-down";
              } else {
                class_html += "desc sprite-icons-up";
              }
              html += "<span class=\"" + class_html + "\">sort</span>";
            }
            html += "</a>";
          }
          html += "</th>";
        }
        html += '</tr>';
        return _this.$thead.html(html);
      };
      if ($.isArray(data)) {
        rows = data;
        total_pages = 0;
      } else if (data.results) {
        rows = data.results;
        total_pages = data.pages || 0;
      } else {
        rows = [];
      }
      this.total_pages = total_pages;
      fillRows(rows);
      fillFooter(total_pages, rows.length);
      return fillHeader();
    },
    _handleClickFirstPage: function(e) {
      this._gotoPage(1);
      return false;
    },
    _handleClickPreviousPage: function(e) {
      this._gotoPage(this.current_page - 1);
      return false;
    },
    _handleClickNextPage: function(e) {
      this._gotoPage(this.current_page + 1);
      return false;
    },
    _handleClickLastPage: function(e) {
      this._gotoPage(this.total_pages);
      return false;
    },
    _gotoPage: function(page) {
      if (page <= this.total_pages) {
        this.current_page = page;
        return this._loadData();
      }
    },
    _clickHeader: function(e) {
      var $th, key;
      $th = $(e.target).closest('th');
      if ($th.length) {
        key = $th.data('key');
        if (key === this.order_by) {
          if (this.sort_order === SortOrder.ASCENDING) {
            this.sort_order = SortOrder.DESCENDING;
          } else {
            this.sort_order = SortOrder.ASCENDING;
          }
        }
        this.order_by = key;
        this.current_page = 1;
        this._loadData();
      }
      return false;
    }
  });

}).call(this);
