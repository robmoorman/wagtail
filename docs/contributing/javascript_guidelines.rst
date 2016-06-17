JavaScript coding guidelines
============================

Wagtail writes JavaScript according it's own ESLint config rules named `eslint-config-wagtail <https://www.npmjs.com/package/eslint-config-wagtail>`_,
which is based upon the rules defined in the `Airbnb Styleguide <http://github.com/airbnb/javascript>`_.


Linting
~~~~~~~

All JavaScript code in the Wagtail codebase is compliant with the specs from the ESLint config. After making a Pull
Request the linter will also check all the JavaScript code, so make sure you checked you changes with ESLint before
you commit your code.

**Running the linter**

Execute ``npm run lint`` to check if your JavaScript code meets the styleguide.


Wagtail React guidelines
~~~~~~~~~~~~~~~~~~~~~~~~

In addition to the JavaScript used in the ``wagtailadmin`` app, we use `React <https://facebook.github.io/react/>`_ to enhance the UI with interactive
components, like the Explorer.

**ES6**

In Wagtail we use `Babel <https://babeljs.io/docs/learn-es2015/>`_ with the ``es2015`` and ``react`` presets.
Especially with React in a combination with Redux we use the following features a lot.

**Arrow functions**

```javascript
// Bad
export const loginSuccess = createAction('LOGIN_SUCCESS', function(email, profile) {
  return { email: email, profile: profile };
});

// Good
export const loginSuccess = createAction('LOGIN_SUCCESS', (email, profile) => {
  return { email, profile };
});
```

Note that we always wrap single arguments with brackets.

* Spread operators (instead of Object.assign)

```javascript
// Bad
case 'LOGIN_SUCCESS':
  return Object.assign({}, state, {
    email: action.payload.email,
    profile: action.payload.profile
  });

// Good
case 'LOGIN_SUCCESS':
  return { ...state, email: action.payload.email, profile: action.payload.profile };
```

**JSX**

All components in Wagtail are written with the `JSX <https://facebook.github.io/react/docs/jsx-in-depth.html>`_ syntax.
Aligment styles are applied as you will see below.

```javascript
// Bad
<Component/>

// Bad
<Component myProperty="foo"
           otherProperty="bar" />

// Good
<Component />

// Good
<Component
  myProperty="foo"
  otherProperty="bar"
/>

// Good (if a single property fits on one line)
<Component myProperty="foo" />
```


**Directory structures**

In Wagtail all components have their own directory (placed in ``client/src/components``), documentation and styles.
A component directory exists at least of the following files (e.g. explorer):

* ``Explorer.js`` (since the component it's named ``Explorer``)
* ``style.scss``
* ``README.md``

If the component is reusable we give them an own directory. It the components only belongs to one other component,
place them in the same directory, e.g. ``ExplorerButton.js`` and ``Explorer.js``.

**Actions**

All actions within Wagtail are created by the `createAction` method of `redux-actions <https://github.com/acdlite/redux-actions>`_.

Actions must be formatted as a `Flux Standard Action <https://github.com/acdlite/flux-standard-action>`_. In this case
an action exists of the following properties.

.. code-block:: javascript

    {
      payload: {
        email: 'foo@bar.com'
      },
      type: 'LOGIN_SUCCESS'
    }

In case of an error, the action should be as you will see below (note that the ``payload`` should be an error object).

.. code-block:: javascript

    {
      error: true,
      payload: new Error('Sorry, the credentials you entered are invalid.'),
      type: 'LOGIN_FAILURE'
    }

An action must not include properties other than ``type``, ``payload``, ``error``, and ``meta``. Since we are using
`redux-action`, these requirements on actions are taken care for us.

Also notice the ``_SUCCESS`` and ``__FAILURE`` appendix in the action name, names with ``__COMPLETE`` or ``_ERROR``
MUST NOT be used instead.

**Redux-actions**

T.b.d.

**Presentational and container components**

Wagtail embraces the idea of seperating presentational and containers components. Presentational components define how
things look, were container components decide how things work (e.g. subscribe to Redux states and dispatch actions).
You can read more about these terms in the `documentation of Redux <http://redux.js.org/docs/basics/UsageWithReact.html>`_.

Presentational components should always be stateless and have to be functions. If you need a local state, implement
lifecycle methods, you can convert them to classes (``class MyComponent extends Component``). In most cases we only use function components.

.. code-block:: javascript

    import { PropTypes } from 'react';

    const MyComponent = ({ username }) => (
      <div>Hello {username}!</div>
    );

    MyComponent.propTypes = {
      username: PropTypes.string.isRequired
    };

    export default MyComponent

Note that we always export a default constant, in this case ``MyComponent``. The name of the constant should always match the filename (``MyComponent.js``).

When it comes to the point our component requires data we create a container component and subscribe to our stores with ``connect()``, as you will see below.

.. code-block:: javascript

  import React, { PropTypes } from 'react';
  import { connect } from 'react-redux';

  class MyContainer extends Component {
    ...
  }

  const mapStateToProps = (state) => {
    ...
  };

  const mapDisPatchToProps = (dispatch) => {
    ...
  };

  export default connect(mapStateToProps, mapDispatchToProps)(MyContainer);
