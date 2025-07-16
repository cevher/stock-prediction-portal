import React from 'react'
import Button from './Button'
import Header from './Header'
import Footer from './Footer'

function Main() {
  return (
      <>
        <div className='container'>
            <div className='p-5 text-center bg-light-dark rounded'>
                <h1 className='text-light'>Stock Prediction Portal to the Stock Prediction Portal</h1>
                <p className='text-light lead'>This is a simple stock prediction portal built with React and Django Rest Framework.</p>
                <Button text='Get Started' class='btn-info' />
            </div>
        </div>
      </>  
)
}

export default Main