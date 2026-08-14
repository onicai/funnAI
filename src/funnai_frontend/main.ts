import App from "./App.svelte"
import "./app.css"
import { startAppVersionPolling } from "./helpers/appVersion"

const app = new App({
  target: document.getElementById("root"),
})

startAppVersionPolling()

export default app

