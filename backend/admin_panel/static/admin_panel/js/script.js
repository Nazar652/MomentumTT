let users = []
let accounts = []
const url = "https://momentum-test-task-ed04e397cbe2.herokuapp.com/api"

const usersResponse = await axios.get(`${url}/users/`)
users = await usersResponse.data

const accountsResponse = await axios.get(`${url}/accounts/`)
accounts = await accountsResponse.data

$(document).ready(function () {
    const usersDiv = $('.users')
    const accountsDiv = $('.accounts')

    for (const user of users) {
        const userDiv = $(document.createElement("div"))
        userDiv.addClass("user")
        userDiv.attr('id', `user-${user.identifier}`)
        userDiv.append(`<div class="first-name cell">${user.first_name}</div>`)
        userDiv.append(`<div class="surname cell">${user.surname}</div>`)
        userDiv.append(`<div class="username cell">${user.username}</div>`)
        userDiv.append(`<div class="identifier cell">${user.identifier}</div>`)
        userDiv.append(`<button class="delete-button delete-user" id="${user.identifier}">Вилучити користувача</button>`)
        usersDiv.append(userDiv)

        $("#user_identifier").append(`<option value="${user.identifier}">${user.first_name}: ${user.identifier}</option>`)
    }
    for (const account of accounts) {
        const accountDiv = $(document.createElement("div"))
        accountDiv.addClass("account")
        accountDiv.attr('id', `account-${account.user}`)
        accountDiv.append(`<div class="phone-number cell">${account.phone_number}</div>`)
        accountDiv.append(`<div class="user-id cell">${account.user}</div>`)
        accountDiv.append(`<button class="delete-button delete-account" id="${account.user}">Вилучити акаунт</button>`)
        accountsDiv.append(accountDiv)
    }

    $('.delete-button').on('click', function () {
        const identifier = $(this).attr('id')
        if ($(this).hasClass('delete-account')){
            axios.delete(`${url}/accounts/delete-by-user/?user=${identifier}`)
            $(this).parent().remove()
        } else {
            axios.delete(`${url}/users/${identifier}`)
            $(`#user-${identifier}`).remove()
            const accountDiv = $(`#account-${identifier}`)
            if (accountDiv.length) {
                axios.delete(`${url}/accounts/delete-by-user/?user=${identifier}`)
                accountDiv.parent().remove()
            }
        }
    })

    $('#create-user').on('click', function () {
        const userData  = {
            first_name: $('#first_name').val(),
            surname: $('#surname').val(),
            username: $('#username').val(),
            identifier: $('#identifier').val()
        }
        axios.post(`${url}/users/`, userData)
    })

    $('#create-account').on('click', function () {
        const accountData  = {
            phone_number: $('#phone_number').val(),
            user: $('#user_identifier').val()
        }

        axios.post(`${url}/accounts/`, accountData)
    })
})

