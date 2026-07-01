import json

# returns dict with color and position consts from theme.json file
def read_theme(theme_path):
    with open(theme_path, 'r') as f:
        data = json.load(f)

    # Resolve screen dimensions from preset + orientation
    screen       = data['screen']
    orientation  = screen.get('orientation', 'portrait')
    preset_name  = screen.get('preset', '240x320')
    preset       = next(p for p in screen['presets'] if p['name'] == preset_name)
    W, H         = preset['w'], preset['h']
    if orientation == 'landscape':
        W, H = H, W

    # Panel pixel heights
    p       = data['layout']['panels']
    art_h   = round(p['art']   * H)
    title_h = round(p['title'] * H)
    seek_h  = round(p['seek']  * H)
    ctrl_h  = round(p['ctrl']  * H)
    vol_h   = H - art_h - title_h - seek_h - ctrl_h

    art_y   = 0
    title_y = art_y   + art_h
    seek_y  = title_y + title_h
    ctrl_y  = seek_y  + seek_h
    vol_y   = ctrl_y  + ctrl_h

    # Control-row buttons
    cb      = data['layout']['ctrl_buttons']
    cb_y_px = round(cb['y_off'] * ctrl_h)
    cb_h_px = round(cb['h']     * ctrl_h)

    def ctrl_btn(key):
        b = cb[key]
        return (round(b['x'] * W), ctrl_y + cb_y_px, round(b['w'] * W), cb_h_px)

    # Volume-row buttons
    vr      = data['layout']['vol_row']
    vr_y_px = round(vr['y_off'] * vol_h)
    vr_h_px = round(vr['h']     * vol_h)

    def vol_btn(key):
        b = vr[key]
        return (round(b['x'] * W), vol_y + vr_y_px, round(b['w'] * W), vr_h_px)

    # Seek / vol bars
    sb = data['layout']['seek_bar']
    vb = data['layout']['vol_bar']

    # Palette: lists → tuples
    palette = {k: tuple(v) for k, v in data['palette'].items()}

    return {
        # screen
        'W': W, 'H': H, 'orientation': orientation,
        # button
        'btn_radius': data['button']['radius'],
        # cover art / visualizer
        'cover_art_mode': data['cover_art']['mode'],
        'n_bars': data['visualizer']['n_bars'],
        'n_segs': data['visualizer']['n_segs'],
        # panels
        'art_y': art_y,     'art_h': art_h,
        'title_y': title_y, 'title_h': title_h,
        'seek_y': seek_y,   'seek_h': seek_h,
        'ctrl_y': ctrl_y,   'ctrl_h': ctrl_h,
        'vol_y': vol_y,     'vol_h': vol_h,
        # control buttons  (x, y, w, h)
        'btn_prev': ctrl_btn('prev'),
        'btn_rev':  ctrl_btn('rev'),
        'btn_play': ctrl_btn('play'),
        'btn_ff':   ctrl_btn('ff'),
        'btn_next': ctrl_btn('next'),
        # volume-row buttons
        'btn_shf':       vol_btn('shf'),
        'btn_rpt':       vol_btn('rpt'),
        'btn_vol_minus': vol_btn('vol_minus'),
        'btn_vol_plus':  vol_btn('vol_plus'),
        # bars  (x, y, w, h)
        'seek_bar': (round(sb['x'] * W), seek_y + round(sb['y_off'] * seek_h),
                     round(sb['w'] * W), round(sb['h'] * seek_h)),
        'vol_bar':  (round(vb['x'] * W), vol_y  + round(vb['y_off'] * vol_h),
                     round(vb['w'] * W), round(vb['h'] * vol_h)),
        **palette,
    }
