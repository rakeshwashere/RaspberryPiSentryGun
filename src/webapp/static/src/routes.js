/* eslint new-cap: 0 */

import React from 'react';
import { Route, Redirect } from 'react-router';

/* containers */
import { App } from './containers/App';
import { HomeContainer } from './containers/HomeContainer';
import LoginView from './components/LoginView';
import RegisterView from './components/RegisterView';
import ProtectedView from './components/ProtectedView';
import Analytics from './components/Analytics';
import NotFound from './components/NotFound';

import { DetermineAuth } from './components/DetermineAuth';
import { requireAuthentication } from './components/AuthenticatedComponent';
import { requireNoAuthentication } from './components/notAuthenticatedComponent';

export default (
    <Route path="/" component={App}>
        {/* <Route path="main" component={requireNoAuthentication(ProtectedView)} /> */}
        {/* <Route path="login" component={requireNoAuthentication(LoginView)} /> */}
        {/* <Route path="register" component={requireNoAuthentication(RegisterView)} /> */}
        <Route path="sentryconsole" component={requireNoAuthentication(HomeContainer)} />
        {/* <Route path="analytics" component={requireNoAuthentication(Analytics)} /> */}
        {/* <Route path="*" component={DetermineAuth(NotFound)} /> */}
        <Redirect to="/sentryconsole" /> 
    </Route>
);
