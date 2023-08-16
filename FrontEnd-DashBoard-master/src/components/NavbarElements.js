import styled from 'styled-components';

export const Nav = styled.nav`
  background: #fff;
  width: 100%;
  padding: 5px 8px;
  border-radius: 5px;
  border: 1px solid #e1e8ee;
  box-shadow: 0 0 5px 0 rgba(0, 0, 0, 0.1);
`;
export const NavTitle = styled.h1`
  width: 100%;
  font-size: 20px;
  color: #009bb0;
  text-align: center;
  font-weight: bold;
  margin-top: 5px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 8px;
  margin-bottom: 0;
`;

export const NavLink = styled.div`
  font-size: 16px;
  text-decoration: none;
  border-bottom: 1px solid #e0e0e0;
  padding: 4px;
  display: block;
  color: #757575;
  cursor: pointer;

  &.active {
    color: #008394;
    font-weight: 600;
    font-size: 20px;
  }

  &:hover {
    color: #008394;
  }
`;

export const SubscriptionNav = styled.div`
  width: 100%;
  background-color: #009bb0;
  border-radius: 5px;
  padding: 8px 12px;
  color: #fff;
  box-shadow: 0 0 5px 0 rgba(0, 0, 0, 0.1);
  font-size: 14px;
`;

export const SubscriptionButton = styled.button`
  border-radius: 20px;
  border: 1px solid #009bb0;
  background-color: #fff;
  color: #009bb0;
  font-size: 14px;
  font-weight: bold;
  padding: 12px 45px;
  letter-spacing: 1px;
  text-transform: uppercase;
  transition: transform 80ms ease-in;
  &:active{
      transform: scale(0.95);
  }
  &:focus {
      outline: none;
  }
`;