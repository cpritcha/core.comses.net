import EditEvent from './edit'

function matchUpdateUrl(pathname) {
    let match = pathname.match(/\/events\/([0-9]+)\/edit\//);
    if (match !== null) {
        match = match[1];
    }
    return match
}

const id = matchUpdateUrl(document.location.pathname);
new EditEvent({ propsData: {id}}).$mount('#app');