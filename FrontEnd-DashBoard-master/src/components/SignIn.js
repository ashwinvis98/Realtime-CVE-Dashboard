import React, {useEffect, useState} from "react";
import * as Components from "./Components";
import axios from "axios";
import "../styles.css";
import { useNavigate } from "react-router-dom";
import Spinner from "react-bootstrap/Spinner";

const REDIRECT_URL = "/dashboard";

const SignIn = () => {
  const [name, setName] = useState(null);
  const [email, setEmail] = useState(null);
  const [password, setPassword] = useState(null);
  const [confirmPassword, setConfirmPassword] = useState(null);
  const [loading, setLoading] = useState(true);
  const [signIn, setSignIn] = useState(null);
  const navigate = useNavigate();

  const handleEmailChange = (event) => {
    let email = event.target.value;
    setEmail(email);
  };

  const handlePasswordChange = (event) => {
    let pass = event.target.value;
    setPassword(pass);
  };

  const toggleIsSignIn = (val) => {
    setSignIn(val);
  };

  const handleConfirmPasswordChange = (event) => {
    let pass = event.target.value;
    setConfirmPassword(pass);
  };

  const handleNameChange = (event) => {
    let name = event.target.value;
    setName(name);
  };

  const callApiSignUP = () => {
    const userData = {
      name: name,
      email: email,
      password: password,
    };

    axios
      .post(window.host + "/api/v1.0/signup", userData)
      .then((response) => {

        if (response.status === 200) {
          localStorage.setItem("user_id", response.data.user_id);
          setSignIn(false);
          navigate(REDIRECT_URL);
        }
      })
      .catch((error) => {
        console.error(error);
      });
    toggleIsSignIn(true);
  };

  const callApiSignIn = async (event) => {
    event.preventDefault();

    const userData = {
      email: email,
      password: password,
    };

    try {
      const response = await axios.post(
        `${window.host}/api/v1.0/login`,
        userData
      );

      if (response.status === 200) {
        localStorage.setItem("user_id", response.data.user_id);
        setSignIn(false);
        navigate(REDIRECT_URL);
      }
    } catch (error) {
      console.log(error);
      alert("Error occurred. Please try again - " + error);
    }
  };

  useEffect(() => {
    if (localStorage.getItem("user_id")) {
      setLoading(true);
      axios.post(window.host + `/api/v1.0/user_session`, {
        user_id: localStorage.getItem("user_id"),
      }).then((response) => {
        if (response.status === 200) {
          setSignIn(false);
          navigate(REDIRECT_URL);
        } else {
          localStorage.removeItem("user_id");
        }
      }).finally(() => {
        setLoading(false);
      });
    } else {
      setLoading(false);
    }
  }, []);

  return (
    <>
      {loading ? (
        <Spinner animation="border" role="status" variant="warning" />
      ) : (
        <div className="h-100 w-100 d-flex flex-column justify-content-center">
          <div className="w-100 d-flex justify-content-center">
            <Components.Container>
              <Components.SignUpContainer signinIn={signIn}>
                <Components.Form>
                  <Components.Title>Create Account</Components.Title>
                  <Components.Input
                    type="text"
                    id="name"
                    placeholder="Name"
                    onChange={handleNameChange}
                  />
                  <Components.Input
                    type="email"
                    id="email"
                    placeholder="Email"
                    onChange={handleEmailChange}
                  />
                  <Components.Input
                    type="password"
                    id="password"
                    placeholder="Password"
                    onChange={handlePasswordChange}
                  />
                  <Components.Input
                    type="password"
                    id="confirmPassword"
                    placeholder="Confirm Password"
                    onChange={handleConfirmPasswordChange}
                  />
                  <Components.Button onClick={callApiSignUP} role="button" type="button">Sign Up</Components.Button>
                </Components.Form>
              </Components.SignUpContainer>

              <Components.SignInContainer signinIn={signIn}>
                <Components.Form>
                  <Components.Title>Sign in</Components.Title>
                  <Components.Input
                    type="email"
                    id="email"
                    placeholder="Email"
                    onChange={handleEmailChange}
                  />
                  <Components.Input
                    type="password"
                    id="password"
                    placeholder="Password"
                    onChange={handlePasswordChange}
                  />
                  <Components.Anchor href="#">Forgot your password?</Components.Anchor>
                  <Components.Button onClick={callApiSignIn} role="button" type="button">Sign In</Components.Button>
                </Components.Form>
              </Components.SignInContainer>

              <Components.OverlayContainer signinIn={signIn}>
                <Components.Overlay signinIn={signIn}>
                  <Components.LeftOverlayPanel signinIn={signIn}>
                    <Components.Title>Welcome Back!</Components.Title>
                    <Components.Paragraph>
                      To keep connected with us please login with your personal info
                    </Components.Paragraph>
                    <Components.GhostButton onClick={() => toggleIsSignIn(true)}>
                      Sign In
                    </Components.GhostButton>
                  </Components.LeftOverlayPanel>

                  <Components.RightOverlayPanel signinIn={signIn}>
                    <Components.Title>Hello, Friend!</Components.Title>
                    <Components.Paragraph>
                      Enter Your personal details and start journey with us
                    </Components.Paragraph>
                    <Components.GhostButton onClick={() => toggleIsSignIn(false)}>
                      Sign Up
                    </Components.GhostButton>
                  </Components.RightOverlayPanel>
                </Components.Overlay>
              </Components.OverlayContainer>
            </Components.Container>
          </div>
        </div>
      )}
    </>
  );
};

export default SignIn;
