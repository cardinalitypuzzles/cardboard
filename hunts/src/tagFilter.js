function getDescendants(tableRow) {
  const allChildren = [tableRow];
  for (let i = 0; i < allChildren.length; i++) {
    const current = allChildren[i];
    Array.prototype.push.apply(allChildren, current.subRows);
  }
  return allChildren;
}

export function addOrRemoveTag(tagList, tag) {
  let tagInList = tagList.filter(x => ['name', 'color', 'id'].every(key => x[key] === tag[key]))[0];
  return (tagInList !== undefined) ? tagList.filter((i) => i !== tagInList) : tagList.concat(tag);
}

export function filterPuzzlesByTagfn(rows, id, filterValue) {
  let requiredRowIDs = rows.filter((row) => {
    return tagList.length === 0 || tagList.some(tag => row.original.tags.map(x => x.id).includes(tag.id));
  }).map(row => row.id);
  // Show metas with puzzles with tags we want? Not sure if this is a good idea.
  let shownRows = rows.filter((row) => {
    return getDescendants(row).some(x => requiredRowIDs.includes(x.id));
  });
  return shownRows;
}
