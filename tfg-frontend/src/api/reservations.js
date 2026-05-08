import client from './client'

export const createReservation = (data) =>
  client.post('/reservations/', data).then((res) => res.data)

export const listRestaurants = () =>
  client.get('/restaurants/').then((res) => res.data)