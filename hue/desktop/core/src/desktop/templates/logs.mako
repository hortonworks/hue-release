## Licensed to Cloudera, Inc. under one
## or more contributor license agreements.  See the NOTICE file
## distributed with this work for additional information
## regarding copyright ownership.  Cloudera, Inc. licenses this file
## to you under the Apache License, Version 2.0 (the
## "License"); you may not use this file except in compliance
## with the License.  You may obtain a copy of the License at
##
##     http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
<%!
from desktop.lib.conf import BoundConfig
from desktop.lib.i18n import smart_unicode
from desktop.views import commonheader, commonfooter
from django.utils.translation import ugettext as _
import re
%>

<%namespace name="actionbar" file="actionbar.mako" />
<%namespace name="layout" file="about_layout.mako" />

${ commonheader(_('About'), "about", user, "100px") | n,unicode }
${layout.menubar(section='log_view')}

<style>
  pre {
    margin: 0;
    padding: 2px;
    border: 0;
  }

  pre.highlighted {
    background-color: yellow;
  }

  pre.highlighted.active {
    background-color: orange;
  }

  #logs {
    overflow: auto;
  }

  #logs pre:first-child {
    padding-top: 10px;
  }

  #logs pre:last-child {
    padding-bottom: 10px;
  }

  .notFound {
    background-color: #f09999 !important;
  }
  .search-handle{
    display: inline-block;
  }
  .search-info{
    display: none;
  }
</style>

<div class="container-fluid">
  <h1>${_('Log entries (most recent first)')}</h1>

  <%actionbar:render>
    <%def name="search()">
        <input type="text" class="input-xxlarge search-query" placeholder="${_('Search...')}" value="${query}">
          <div class="btn-group search-handle">
            <input type="button" class="prev btn btn-mini disabled" value="Prev"></input>
            <input type="button" class="next btn btn-mini disabled" value="Next"></input>
          </div>
        <input type="button" class="update btn btn-mini" value="Update"></input>
        <span class="search-info help-inline"><span class="cur"></span> of <span class="com"></span></span>
    </%def>
    <%def name="creation()">
        <span class="btn-group">
          <a href="/download_logs" class="btn"><i class="icon-download-alt"></i> ${_('Download entire log as zip')}</a>
        </span>
    </%def>
  </%actionbar:render>

  <% log.reverse() %>

  <div id="logs">
      % for l in log:
        <pre>${smart_unicode(l, errors='ignore')}</pre>
      % endfor
  </div>

</div>

<script>
  $(document).ready(function () {

    resizeScrollingLogs();

    var resizeTimeout = -1;
    $(window).resize(function () {
      window.clearTimeout(resizeTimeout);
      resizeTimeout = window.setTimeout(function () {
        resizeScrollingLogs();
      }, 200);
    });

    var filterTimeout = searchTimeout = -1;
    var matches = [];
    $(".search-query").keyup(function (e) {
      if (e.keyCode=='13' && matches.length > 0) {
        window.clearTimeout(searchTimeout);
        searchTimeout = window.setTimeout(toNextMatch, 50);
      } else {
        window.clearTimeout(filterTimeout);
        filterTimeout = window.setTimeout(function () {
          filterLogs($(".search-query").val());
        }, 500);
      }
    });

    if ("${query}" != "") {
      filterLogs("${query}");
    }

    $('#logs').on('click','.highlighted',function () {
      if (!$(this).hasClass('active')) {
        $('pre.highlighted.active').removeClass('active');
        $(this).addClass('active');
        for (var el in matches) {
          i = parseInt(el);
          if ($(matches[i]).hasClass('active')) {
            $('.search-info').find('.cur').text(i+1);
            return false;
          }
        }
      }
    });

    function updateLogs () {
      $.post('/logs',function(data){
        $('#logs').html('');
        for (var i = data.log.length - 1; i >= 0; i--) {
          $('<pre>').text(data.log[i]).appendTo($('#logs'));
        };
        filterLogs($(".search-query").val());
      },'json').error(function() {
        window.location.reload(true);
      });
    }

    $('.prev').on('click',{'dir':'prev'},toNextMatch);
    $('.next').on('click',{'dir':'next'},toNextMatch);
    $('.update').on('click',updateLogs);

    function toNextMatch(_arg) {
      var arg=_arg||'next'; 
      var dir=(arg.data)?arg.data.dir||'next':arg;
      var i = 0,nextMatch;
      for (var el in matches) {
        i = parseInt(el);
        if ($(matches[i]).hasClass('active')) {
          $(matches[i]).removeClass('active');
          var ni=(dir=='next')?i+1:i-1;
          if (matches[ni]) {
            nextMatch=$(matches[ni]);
          } else {
            ni=(dir=='next')?0:matches.length-1;
            nextMatch=$(matches[ni])
          }
          $('.search-info').find('.cur').text(ni+1);
          nextMatch.addClass('active');
          scrollToMatch(nextMatch)
          return false;
        }
      }
    }

    function resizeScrollingLogs() {
      var _el = $("#logs");
      if (!$.browser.msie) {
        _el.css("overflow-y", "").css("height", "");
      }
      var heightAfter = 0;
      _el.nextAll(":visible").each(function () {
        heightAfter += $(this).outerHeight(true);
      });
      if (_el.height() > ($(window).height() - _el.offset().top - heightAfter)) {
        _el.css("overflow-y", "auto").height($(window).height() - _el.offset().top - heightAfter);
      }
    }

    function filterLogs(query) {
      $("pre.highlighted").removeClass("highlighted active");
      $(".search-query").removeClass("notFound");
      $('.search-handle .btn').addClass('disabled');
      $('.search-info').hide().find('span').text('');
      if ($.trim(query) == "") {
        $("#logs").scrollTop(0);
        return false;
      }
      matches = [];
      $("#logs pre").each(function () {
        if ($(this).text().toLowerCase().replace(/\s/g, "").indexOf(query.toLowerCase().replace(/\s/g, "")) > -1) {
          matches.push(this);
        }
      });
      if (matches.length > 0) {
        $('.search-info').show().find('.com').text(matches.length).parent().find('.cur').text('1');
        $(matches).addClass("highlighted").first().addClass("active");
        $('.search-handle .btn').removeClass('disabled');
        scrollToMatch($(matches).first())
      }
      if (matches.length < 1) {
        $(".search-query").addClass("notFound");
        $("#logs").scrollTop(0);
      }
    }

    function scrollToMatch (match) {
      var scrollVal = $("#logs")[0].scrollTop+match.offset().top-$("#logs").position().top-$('#logs').height()/2+15;
      $("#logs").animate({scrollTop:scrollVal}, {duration: 100 });
    }

  });
</script>

${ commonfooter(messages) | n,unicode }
