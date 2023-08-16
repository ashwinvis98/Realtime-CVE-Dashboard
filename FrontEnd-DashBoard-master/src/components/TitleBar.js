import React from 'react';
import styled from 'styled-components';
// import {
// Nav,
// NavLink,
// Bars,
// NavMenu,
// NavBtn,
// NavBtnLink,
// } from './NavbarElements';

const Title = styled.div`
	background-color: #009bb0;
	height: 60px;
	width: 100%;
	display: flex;
	justify-content: start;
	padding: 8px 10px 10px 20px;
`

const TitleContent = styled.div`
  color: #fff;
  font-size: 25px;
  font-weight: bold;
	display: flex;
	flex-direction: column;
  justify-content: center;
	height: 100%;
`

const TitleBar = () => {
return (
	<Title>
		<TitleContent>CVE Live</TitleContent>
	</Title>
);
};

export default TitleBar;
