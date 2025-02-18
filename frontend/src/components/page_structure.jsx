import React from 'react';
import './styles/components.css';
import Banner from './banner.jsx';
import Body from './body_structure.jsx'


const Page = () => {

    return (
        <>
            <div className='page'>
                <Banner />
                <Body />
            </div>
            
        </>
    )
}

export default Page;
