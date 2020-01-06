// Licensed to Cloudera, Inc. under one
// or more contributor license agreements.  See the NOTICE file
// distributed with this work for additional information
// regarding copyright ownership.  Cloudera, Inc. licenses this file
// to you under the Apache License, Version 2.0 (the
// "License"); you may not use this file except in compliance
// with the License.  You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import $ from 'jquery';
import * as ko from 'knockout';

import apiHelper from 'api/apiHelper';
import hueAnalytics from 'utils/hueAnalytics';
import huePubSub from 'utils/huePubSub';
import I18n from 'utils/i18n';
import {
  CONFIG_REFRESHED_EVENT,
  GET_KNOWN_CONFIG_EVENT,
  REFRESH_CONFIG_EVENT
} from 'utils/hueConfig';

class TopNavViewModel {
  constructor(onePageViewModel) {
    const self = this;
    self.onePageViewModel = onePageViewModel;
    self.leftNavVisible = ko.observable(false);
    self.leftNavVisible.subscribe(val => {
      huePubSub.publish('left.nav.open.toggle', val);
      hueAnalytics.convert('hue', 'leftNavVisible/' + val);
      if (val) {
        // Defer or it will be triggered by the open click
        window.setTimeout(() => {
          $(document).one('click', () => {
            if (self.leftNavVisible()) {
              self.leftNavVisible(false);
            }
          });
        }, 0);
      }
    });

    huePubSub.subscribe('hue.toggle.left.nav', self.leftNavVisible);

    // TODO: Drop. Just for PoC
    self.pocClusterMode = ko.observable();
    apiHelper.withTotalStorage('topNav', 'multiCluster', self.pocClusterMode, 'dw');
    huePubSub.subscribe('set.multi.cluster.mode', self.pocClusterMode);

    self.onePageViewModel.currentApp.subscribe(() => {
      self.leftNavVisible(false);
    });

    self.mainQuickCreateAction = ko.observable();
    self.quickCreateActions = ko.observableArray();

    self.hasJobBrowser = ko.observable(window.HAS_JOB_BROWSER);
    self.clusters = ko.observableArray();

    const configUpdated = config => {
      if (config && config['main_button_action']) {
        const topApp = config['main_button_action'];
        self.mainQuickCreateAction({
          displayName: topApp.buttonName,
          icon: topApp.type,
          tooltip: topApp.tooltip,
          url: topApp.page
        });
      } else {
        self.mainQuickCreateAction(undefined);
      }

      if (config && config['button_actions']) {
        const apps = [];
        const buttonActions = config['button_actions'];
        buttonActions.forEach(app => {
          const interpreters = [];
          let toAddDivider = false;
          let dividerAdded = false;
          let lastInterpreter = null;
          $.each(app['interpreters'], (index, interpreter) => {
            // Promote the first catagory of interpreters
            if (!dividerAdded) {
              toAddDivider =
                (app.name === 'editor' || app.name === 'dashboard') &&
                (lastInterpreter != null && lastInterpreter.is_sql != interpreter.is_sql);
            }
            interpreters.push({
              displayName: interpreter.displayName,
              dividerAbove: toAddDivider,
              icon: interpreter.type,
              url: interpreter.page
            });
            lastInterpreter = interpreter;
            if (toAddDivider) {
              dividerAdded = true;
              toAddDivider = false;
            }
          });

          if (window.SHOW_ADD_MORE_EDITORS && app.name === 'editor' && interpreters.length > 1) {
            interpreters.push({
              displayName: I18n('Add more...'),
              dividerAbove: true,
              href: 'https://docs.gethue.com/administrator/configuration/connectors/'
            });
          }

          apps.push({
            displayName: app.displayName,
            icon: app.name,
            isCategory: interpreters.length > 0,
            children: interpreters,
            url: app.page
          });
        });

        self.quickCreateActions(apps);
      } else {
        self.quickCreateActions([]);
      }

      if (config && config['clusters']) {
        self.clusters(config['clusters']);
      }

      self.hasJobBrowser(
        window.HAS_JOB_BROWSER &&
          config &&
          config['app_config'] &&
          config['app_config']['browser'] &&
          (config['app_config']['browser']['interpreter_names'].indexOf('yarn') !== -1 ||
            config['app_config']['editor']['interpreter_names'].indexOf('impala') !== -1 ||
            config['app_config']['browser']['interpreter_names'].indexOf('dataeng') !== -1)
      );
    };

    huePubSub.publish(GET_KNOWN_CONFIG_EVENT, configUpdated);
    huePubSub.subscribe(CONFIG_REFRESHED_EVENT, configUpdated);

    huePubSub.subscribe('hue.new.default.app', () => {
      huePubSub.publish(REFRESH_CONFIG_EVENT);
    });
  }
}

export default TopNavViewModel;
