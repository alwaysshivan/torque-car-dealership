import React from 'react';
import {it,expect,vi} from 'vitest';
import {render,screen,fireEvent} from '@testing-library/react';
import App from './App';
it('starts at secure sign-in and lets visitors open registration',()=>{
  render(<App/>);
  expect(screen.getByRole('heading',{name:/welcome back/i})).toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:/create an account/i}));
  expect(screen.getByLabelText('Full name')).toBeRequired();
  expect(screen.getByRole('button',{name:'Create account'})).toBeInTheDocument();
});
it('shows a useful message when the server is unavailable',async()=>{
  vi.stubGlobal('fetch',vi.fn().mockRejectedValue(new Error('Network unavailable')));
  render(<App/>);
  fireEvent.change(screen.getByLabelText('Email address'),{target:{value:'siva@example.com'}});
  fireEvent.change(screen.getByLabelText('Password'),{target:{value:'StrongPass123!'}});
  fireEvent.submit(screen.getByRole('button',{name:'Sign in'}).closest('form'));
  expect(await screen.findByRole('alert')).toHaveTextContent('Network unavailable');
  vi.unstubAllGlobals();
});
