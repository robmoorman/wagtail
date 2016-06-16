JavaScript coding guidelines
============================

Write JavaScript according to the `Airbnb Styleguide <http://github.com/airbnb/javascript>`_, with some exceptions:

-  Use soft-tabs with a four space indent. Spaces are the only way to
   guarantee code renders the same in any person's environment.
-  We accept ``snake_case`` in object properties, such as
   ``ajaxResponse.page_title``, however camelCase or UPPER_CASE should be used
   everywhere else.


Linting and formatting code
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Wagtail provides some tooling configuration to help check your code meets the
styleguide. You'll need node.js and npm on your development machine.
Ensure project dependencies are installed by running ``npm install``


**Linting code**

``npm run lint:js``

This will lint all the JS in the wagtail project, excluding vendor
files and compiled libraries.

Some of the modals are generated via server-side scripts. These include
template tags that upset the linter, so modal workflow JavaScript is
excluded from the linter.


**Formatting code**

``npm run format:js``

This will perform safe edits to conform your JS code to the styleguide.
It won't touch the line-length, or convert quotemarks from double to single.

Run the linter after you've formatted the code to see what manual fixes
you need to make to the codebase.

**Changing the linter configuration**

Under the hood, the tasks use the `JavaScript Code Style <http://jscs.info/>`_ library.

To edit the settings for ignored files, or to change the linting rules,
edit the ``.jscsrc`` file in the wagtail project root.

A complete list of the possible linting rules can be found here:
`JSCS Rules <http://jscs.info/rules.html>`_


Wagtail React guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

**Directory structures**

T.b.d.

**Actions**

All actions within Wagtail are available via actionCreators.

Actions must be formatted as a `Flux Standard Action<https://github.com/acdlite/flux-standard-action>`_. In this case
an action exists of the following properties.

```javascript
{
  payload: {
    email: 'foo@bar.com'
  },
  type: 'LOGIN_SUCCESS'
}
```

In case of an error, the action should be as you will see below (note that the ``payload`` should be an error object).

```javascript
{
  error: true,
  payload: new Error('Sorry, the credentials you entered are invalid.'),
  type: 'LOGIN_FAILURE'
}
```

An action must not include properties other than ``type``, ``payload``, ``error``, and ``meta``.

**Presentational and container components**

Wagtail embraces the idea of seperating presentational and containers components. Presentational components define how
things look, were container components decide how things work (e.g. subscribe to Redux states and dispatch actions).
You can read more about these terms in the `documentation of Redux <http://redux.js.org/docs/basics/UsageWithReact.html>`_.

Presentational components should always be stateless and have to be functions. If you need a local state, implement
lifecycle methods, you can convert them to classes (``class MyComponent extends Component``). In most cases we only use function components.

```javascript
import { PropTypes } from 'react';

const MyComponent = ({ username }) => (
  <div>Hello {username}!</div>
);

MyComponent.propTypes = {
  username: PropTypes.string.isRequired
};

export default MyComponent
```

Note that we always export a default constants, in this case ``MyComponent``. The name of the constant should always match the filename (``MyComponent.js``).

When it comes to the point our component requires data we create a container component and subscribe to our stores with ``connect()``, as you will see below.

```javascript
import React, { PropTypes } from 'react';
import { connect } from 'react-redux';

class MyContainer extends Component {
  ...
}

const connect = (state) => {
  ...
};

const mapDisPatchToProps = (dispatch) => {
  ...
};

export default connect(mapStateToProps, mapDispatchToProps)(MyContainer);

```
