import React from 'react';
import { Link } from 'react-router-dom';

class Header extends React.Component {

    render() {
        return (
            <nav class="navbar navbar-expand-lg navbar-light bg__nav--white">
                <div class='container mb-2 mt-2'>
                    <a class="navbar-brand header__logo header__logo--theme mb-1" href="/">
                        sxftware
                    </a>
                    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar-nav-alt-markup" aria-controls="navbar-nav-alt-markup" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon"></span>
                    </button>
                    <div class="collapse navbar-collapse" id="navbar-nav-alt-markup">
                        <ul class="navbar-nav mr-auto">
                            <li class="nav-item {% if request.url_rule.rule == '/about' %} active {% endif %}"><a class="nav-link nav__navlink--center" href="{{ url_for('home.about') }}">Start Here</a></li>
                            <li class="nav-item {% if request.url_rule.rule == '/pricing' %} active {% endif %}"><a class="nav-link nav__navlink--center" href="{{ url_for('home.pricing') }}">Pricing</a></li>
                        </ul>
                        <ul class="navbar-nav">
                            <li class="nav-item {% if request.url_rule.rule == '/login' %} active {% endif %}"><a class="nav-link nav__navlink--center mr-3" href="{{ url_for('auth.login') }}">Sign in</a></li>
                            <li class="nav-item"><a class="nav-item btn button-Primary text__tranform--uppercase" href="{{ url_for('auth.signup') }}">Get started</a></li>
                        </ul>
                    </div>
                </div>
            </nav>
        )
    }
}

export default Header;